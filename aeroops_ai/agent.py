import json
import re
from typing import Any
from pydantic import BaseModel, Field
from google.adk.workflow import Workflow, node, JoinNode
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.agents import LlmAgent
from google.adk.agents.context import Context

from .config import MODEL_NAME, HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD, DEMO_MODE
from .security import validate_flight_request, detect_prompt_injection, redact_sensitive_pi

# =====================================================================
# 1. Pydantic Schemas
# =====================================================================

class FlightOpsRequest(BaseModel):
    origin_airport: str = Field(description="Origin IATA/ICAO airport code (e.g. SFO)")
    destination_airport: str = Field(description="Destination IATA/ICAO airport code (e.g. LAX)")
    flight_number: str = Field(description="Flight number (e.g. UA123)")
    scheduled_time: str = Field(description="Scheduled departure/arrival time in ISO 8601 format")
    notam_text: str = Field(description="Raw NOTAM (Notice to Air Missions) text")
    weather_text: str = Field(description="Raw meteorological/weather forecast text (METAR/TAF)")
    operational_notes: str = Field(description="Additional operational or crew notes")

class ValidationOutcome(BaseModel):
    is_valid: bool = Field(description="Whether the request is valid")
    errors: list[str] = Field(default=[], description="List of validation error messages")
    security_flagged: bool = Field(default=False, description="Whether prompt injection or security threat was flagged")
    redacted_categories: list[str] = Field(default=[], description="PII categories that were redacted")

class NOTAMAnalysis(BaseModel):
    critical_notams: list[str] = Field(default_factory=list, description="List of critical NOTAM hazards or closures identified")
    notam_summary: str = Field(default="No significant operational NOTAM restrictions detected.", description="Clean, decoded summary of all NOTAMs in plain English")
    impact_level: str = Field(default="LOW", description="NOTAM impact level: LOW, MEDIUM, or HIGH")

class WeatherAnalysis(BaseModel):
    hazardous_conditions: list[str] = Field(default_factory=list, description="List of hazardous weather phenomena (e.g. icing, windshear)")
    weather_summary: str = Field(default="No significant weather hazards detected.", description="Clean summary of the weather conditions in plain English")
    impact_level: str = Field(default="LOW", description="Weather impact level: LOW, MEDIUM, or HIGH")

class RiskAssessment(BaseModel):
    detected_risks: list[str] = Field(description="Consolidated list of operational risks")
    risk_score: int = Field(description="Deterministic risk score from 0 to 100")
    risk_level: str = Field(description="Risk level: LOW, MEDIUM, or HIGH")
    recommended_action: str = Field(description="Recommended action: PROCEED, RE-ROUTE, HOLD, or CANCEL")
    needs_human_review: bool = Field(description="True if risk_level is HIGH or security was flagged")

class HumanReviewResult(BaseModel):
    approved: bool = Field(description="Whether the flight briefing is approved by the human reviewer")
    reviewer_comments: str = Field(description="Feedback, adjustments, or comments from the reviewer")

class FlightBriefing(BaseModel):
    operational_summary: str = Field(description="Consolidated operational summary of the flight")
    detected_risks: list[str] = Field(description="List of all detected risks from NOTAM and weather")
    risk_score: int = Field(description="Final operational risk score (0-100)")
    risk_level: str = Field(description="Final risk level classification")
    recommended_action: str = Field(description="Final recommended operational action")
    final_briefing_text: str = Field(description="Complete flight briefing text for the cockpit crew")
    human_reviewed: bool = Field(default=False, description="Whether human review was performed")
    reviewer_comments: str | None = Field(default=None, description="Comments from the human reviewer, if any")

# =====================================================================
# 2. Input Validation and Security Node (FunctionNode)
# =====================================================================

@node
def validate_input(node_input: Any) -> Event:
    """Security Layer: Validates input, scans for prompt injection, and redacts PII."""
    
    # Standardize input to dict
    raw_data = {}
    if hasattr(node_input, "parts") and len(node_input.parts) > 0:
        # If passed as ADK Content object, try parsing text as JSON
        text = node_input.parts[0].text
        try:
            raw_data = json.loads(text)
        except Exception:
            # If not JSON, map simple text to notes or handle as raw dict if possible
            raw_data = {"operational_notes": text}
    elif isinstance(node_input, dict):
        raw_data = node_input
    elif isinstance(node_input, str):
        try:
            raw_data = json.loads(node_input)
        except Exception:
            raw_data = {"operational_notes": node_input}
            
    # Step A: Validate input fields
    errors = validate_flight_request(raw_data)
    if errors:
        outcome = ValidationOutcome(is_valid=False, errors=errors)
        return Event(output=outcome, route="invalid")
        
    # Step B: Security scan - Check for prompt injection in all text fields
    notam_raw = raw_data.get("notam_text", "")
    weather_raw = raw_data.get("weather_text", "")
    notes_raw = raw_data.get("operational_notes", "")
    
    security_flagged = (
        detect_prompt_injection(notam_raw) or 
        detect_prompt_injection(weather_raw) or 
        detect_prompt_injection(notes_raw)
    )
    
    # Step C: PII Redaction & Sanitization
    clean_notam, redacted_notam = redact_sensitive_pi(notam_raw)
    clean_weather, redacted_weather = redact_sensitive_pi(weather_raw)
    clean_notes, redacted_notes = redact_sensitive_pi(notes_raw)
    
    # If injection detected, sanitize the inputs to prevent downstream exploit
    if security_flagged:
        clean_notam = "[POTENTIAL PROMPT INJECTION DETECTED AND BLOCKED]"
        clean_weather = "[POTENTIAL PROMPT INJECTION DETECTED AND BLOCKED]"
        clean_notes = "[POTENTIAL PROMPT INJECTION DETECTED AND BLOCKED]"
        
    redacted_categories = list(set(redacted_notam + redacted_weather + redacted_notes))
    
    sanitized_request = FlightOpsRequest(
        origin_airport=raw_data["origin_airport"].upper(),
        destination_airport=raw_data["destination_airport"].upper(),
        flight_number=raw_data["flight_number"].upper(),
        scheduled_time=raw_data["scheduled_time"],
        notam_text=clean_notam,
        weather_text=clean_weather,
        operational_notes=clean_notes
    )
    
    state_delta = {
        "flight_request": sanitized_request.model_dump(),
        "security_flagged": security_flagged,
        "redacted_categories": redacted_categories
    }
    
    route_name = "security_flag" if security_flagged else "valid"
    return Event(output=sanitized_request, route=route_name, state=state_delta)

@node
def validation_failure(node_input: ValidationOutcome) -> FlightBriefing:
    """Handles parsing and validation errors, generating a structured failure response."""
    error_summary = "; ".join(node_input.errors)
    return FlightBriefing(
        operational_summary="FLIGHT OPS REQUEST REJECTED: VALIDATION FAILED",
        detected_risks=node_input.errors,
        risk_score=100,
        risk_level="HIGH",
        recommended_action="CANCEL",
        final_briefing_text=f"Flight planning aborted due to input validation failures: {error_summary}"
    )

# =====================================================================
# 3. Parallel Analysis Agents (LlmAgents)
# =====================================================================

notam_analyst = LlmAgent(
    name="notam_analyst",
    model=MODEL_NAME,
    instruction="""You are an expert Flight Operations Dispatcher specializing in NOTAM analysis.
Analyze the provided FlightOpsRequest. Review the NOTAM text (Notice to Air Missions).
Identify critical runway/taxiway closures, airport shutdowns, equipment outages (e.g. ILS/radar), or airspace restrictions.
Extract a list of critical NOTAM hazards, summarize all NOTAM details clearly, and assign a NOTAM impact level:
- HIGH: Airport closed, primary runway closed, or critical navigation aid offline in low visibility.
- MEDIUM: Secondary runway closed, major taxiway closed, or significant operations restrictions.
- LOW: Minor taxiway/apron closed, obstruction lights out, or general information warnings.
""",
    output_schema=NOTAMAnalysis,
)

weather_analyst = LlmAgent(
    name="weather_analyst",
    model=MODEL_NAME,
    instruction="""You are an aviation meteorologist.
Analyze the provided FlightOpsRequest. Review the weather text (METAR, TAF, SIGMETs).
Identify hazardous weather conditions such as convective storms, severe winds, low visibility/ceilings, wind shear, icing, or turbulence.
Extract a list of hazardous weather conditions, summarize the weather clearly, and assign a weather impact level:
- HIGH: Severe thunderstorms, active wind shear, visibility below minimums, severe icing/turbulence.
- MEDIUM: Moderate rain/snow, gusty crosswinds, low ceilings, moderate icing/turbulence.
- LOW: Clear skies, light winds, unrestricted visibility.
""",
    output_schema=WeatherAnalysis,
)

join_analyses = JoinNode(name="join_analyses")

# =====================================================================
# 4. Deterministic Risk Assessment Node (FunctionNode)
# =====================================================================

@node
def assess_risk(ctx: Context, node_input: dict[str, Any]) -> RiskAssessment:
    """Computes a deterministic risk score and classification in Python code."""
    
    # Retrieve raw analysis outputs from preceding joined nodes
    notam_data = node_input.get("notam_analyst", {})
    weather_data = node_input.get("weather_analyst", {})
    
    # Convert dictionaries back to model objects (due to JoinNode dict serialization)
    notam_analysis = NOTAMAnalysis(**notam_data) if isinstance(notam_data, dict) else notam_data
    weather_analysis = WeatherAnalysis(**weather_data) if isinstance(weather_data, dict) else weather_data
    
    security_flagged = ctx.state.get("security_flagged", False)
    
    # Deterministic Scoring Algorithm
    risk_score = 10  # Base score
    detected_risks = []
    
    # A. NOTAM Impact Points
    if notam_analysis.impact_level == "HIGH":
        risk_score += 35
        detected_risks.append("CRITICAL NOTAM: High operational restriction detected")
    elif notam_analysis.impact_level == "MEDIUM":
        risk_score += 20
        detected_risks.append("NOTAM Warning: Moderate operational restriction detected")
        
    # B. Weather Impact Points
    if weather_analysis.impact_level == "HIGH":
        risk_score += 35
        detected_risks.append("HAZARDOUS WEATHER: High risk weather detected")
    elif weather_analysis.impact_level == "MEDIUM":
        risk_score += 20
        detected_risks.append("Weather Warning: Moderate risk weather detected")
        
    # C. Density of issues
    if len(notam_analysis.critical_notams) > 2:
        risk_score += 10
        detected_risks.append(f"Multiple NOTAMs ({len(notam_analysis.critical_notams)}) active")
        
    if len(weather_analysis.hazardous_conditions) > 2:
        risk_score += 10
        detected_risks.append(f"Multiple weather hazards ({len(weather_analysis.hazardous_conditions)}) active")
        
    # D. Security violations override
    if security_flagged:
        risk_score = 100
        detected_risks.append("SECURITY EVENT: Prompt injection attempt detected")
        
    # Cap score between 0 and 100
    risk_score = min(max(risk_score, 0), 100)
    
    # Determine risk level deterministically
    if risk_score >= HIGH_RISK_THRESHOLD:
        risk_level = "HIGH"
    elif risk_score >= MEDIUM_RISK_THRESHOLD:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
        
    # Determine recommended action deterministically
    if risk_level == "HIGH":
        recommended_action = "CANCEL" if security_flagged else "HOLD"
    elif risk_level == "MEDIUM":
        recommended_action = "RE-ROUTE"
    else:
        recommended_action = "PROCEED"
        
    needs_human_review = (risk_level == "HIGH") or security_flagged
    
    assessment = RiskAssessment(
        detected_risks=detected_risks,
        risk_score=risk_score,
        risk_level=risk_level,
        recommended_action=recommended_action,
        needs_human_review=needs_human_review
    )
    
    # Save the assessment in state
    ctx.state["risk_assessment"] = assessment.model_dump()
    ctx.state["notam_summary"] = notam_analysis.notam_summary
    ctx.state["weather_summary"] = weather_analysis.weather_summary
    
    return assessment

# =====================================================================
# 5. Routing and Human-in-the-Loop Node (FunctionNodes)
# =====================================================================

@node
def route_risk(node_input: RiskAssessment) -> Event:
    """Routes the workflow based on deterministic human review requirements."""
    if node_input.needs_human_review:
        return Event(output=node_input, route="human_review")
    return Event(output=node_input, route="direct_briefing")

@node(rerun_on_resume=True)
async def human_review(ctx: Context, node_input: RiskAssessment) -> Event:
    """Suspends the workflow for manual operational review on HIGH risk/security cases."""
    request_data = ctx.state.get("flight_request", {})
    
    if not ctx.resume_inputs:
        message = (
            f"⚠️ HIGH RISK FLIGHT OPERATIONS DETECTED (Score: {node_input.risk_score}/100, Level: {node_input.risk_level})\n"
            f"Flight: {request_data.get('flight_number')} from {request_data.get('origin_airport')} to {request_data.get('destination_airport')}\n"
            f"Detected Risks: {', '.join(node_input.detected_risks)}\n"
            f"NOTAM Summary: {ctx.state.get('notam_summary')}\n"
            f"Weather Summary: {ctx.state.get('weather_summary')}\n\n"
            f"Action proposed: {node_input.recommended_action}\n"
            f"Please respond with 'approve' or 'override: <new recommended action>', followed by any comments."
        )
        yield RequestInput(interrupt_id="human_decision", message=message)
        return
        
    raw_decision = ctx.resume_inputs.get("human_decision", "")
    if isinstance(raw_decision, dict):
        decision_text = raw_decision.get("decision") or raw_decision.get("human_decision") or next(iter(raw_decision.values()), "")
    else:
        decision_text = str(raw_decision)
    decision_text = decision_text.strip()
    
    # Parse decision
    approved = True
    comments = decision_text
    overridden_action = None
    
    decision_lower = decision_text.lower()
    if "override:" in decision_lower:
        approved = True
        match = re.search(r"override:\s*(\w+)", decision_text, re.IGNORECASE)
        if match:
            overridden_action = match.group(1).upper()
    elif "reject" in decision_lower or "cancel" in decision_lower or "deny" in decision_lower:
        approved = False
        
    review_outcome = HumanReviewResult(
        approved=approved,
        reviewer_comments=comments
    )
    
    state_delta = {
        "human_review": review_outcome.model_dump()
    }
    if overridden_action:
        state_delta["overridden_action"] = overridden_action
        
    yield Event(output=review_outcome, state=state_delta)

# =====================================================================
# 6. Consolidated Briefing Generator (LlmAgent & Helper Node)
# =====================================================================

@node
def prepare_briefing_prompt(ctx: Context, node_input: Any) -> str:
    """Prepares a unified JSON string payload to feed into the Briefing Generator Agent."""
    request_data = ctx.state.get("flight_request", {})
    risk_data = ctx.state.get("risk_assessment", {})
    notam_summary = ctx.state.get("notam_summary", "")
    weather_summary = ctx.state.get("weather_summary", "")
    
    human_review = ctx.state.get("human_review")
    overridden_action = ctx.state.get("overridden_action")
    
    # Merge human decision/overrides if applicable
    final_action = risk_data.get("recommended_action")
    if overridden_action:
        final_action = overridden_action
    elif human_review and not human_review.get("approved"):
        final_action = "CANCEL"
        
    briefing_payload = {
        "flight_details": request_data,
        "risk_assessment": {
            **risk_data,
            "recommended_action": final_action
        },
        "notam_summary": notam_summary,
        "weather_summary": weather_summary,
        "human_review": human_review
    }
    
    return json.dumps(briefing_payload, indent=2)

briefing_generator = LlmAgent(
    name="briefing_generator",
    model=MODEL_NAME,
    instruction="""You are a Senior Flight Dispatcher. Synthesize the provided flight ops data, analysis summaries, and risk assessments into a final FlightBriefing.
You MUST write:
1. An operational summary outlining the routing, flight number, time, and key risk levels.
2. A comprehensive, formatted briefing text tailored for the flight crew (cockpit).
3. If human review was performed, mention the reviewer's inputs or overrides and integrate them into the recommended action and briefing notes.
4. Ensure the output fits the output_schema exactly.
""",
    output_schema=FlightBriefing,
)

# =====================================================================
# Mock functions for DEMO_MODE
# =====================================================================

@node(name="notam_analyst")
def mock_notam_analyst(node_input: FlightOpsRequest) -> NOTAMAnalysis:
    """Mock NOTAM analyst for DEMO_MODE with keyword-based aviation risk detection."""
    notam_text = node_input.notam_text or ""
    text = notam_text.lower()

    if "potential prompt injection" in text:
        return NOTAMAnalysis(
            critical_notams=[],
            notam_summary="[DEMO MODE] Security Block: Raw NOTAM replaced due to security event.",
            impact_level="LOW"
        )

    critical_notams = []

    if "rwy" in text or "runway" in text:
        if "closed" in text or "clsd" in text:
            critical_notams.append("Runway closure detected")

    if "taxiway" in text or "twy" in text:
        if "restricted" in text or "closed" in text or "clsd" in text:
            critical_notams.append("Taxiway restriction detected")

    if "ground delay" in text or "ground delays" in text:
        critical_notams.append("Ground delay risk detected")

    if "ad clsd" in text or "aerodrome closed" in text or "airport closed" in text:
        critical_notams.append("Aerodrome closure detected")

    if critical_notams:
        return NOTAMAnalysis(
            critical_notams=critical_notams,
            notam_summary="[DEMO MODE] Operational NOTAM restrictions detected: " + "; ".join(critical_notams),
            impact_level="HIGH"
        )

    return NOTAMAnalysis(
        critical_notams=[],
        notam_summary="[DEMO MODE] No critical NOTAMs identified.",
        impact_level="LOW"
    )


@node(name="weather_analyst")
def mock_weather_analyst(node_input: FlightOpsRequest) -> WeatherAnalysis:
    """Mock weather analyst for DEMO_MODE with keyword-based weather risk detection."""
    weather_text = node_input.weather_text or ""
    text = weather_text.lower()

    if "potential prompt injection" in text:
        return WeatherAnalysis(
            hazardous_conditions=[],
            weather_summary="[DEMO MODE] Security Block: Raw weather text replaced due to security event.",
            impact_level="LOW"
        )

    hazardous_conditions = []

    if "tsra" in text or "thunderstorm" in text or "storm" in text:
        hazardous_conditions.append("Thunderstorm activity detected")

    if "strong" in text and "wind" in text:
        hazardous_conditions.append("Strong winds detected")

    if "gust" in text or "g25" in text or "g30" in text or "g38" in text or "g40" in text:
        hazardous_conditions.append("Gusty wind conditions detected")

    if "crosswind" in text:
        hazardous_conditions.append("Crosswind risk detected")

    if "42" in text or "41" in text or "45" in text or "high temperature" in text:
        hazardous_conditions.append("High ambient temperature detected")

    if hazardous_conditions:
        impact_level = "HIGH" if any(x in h for h in hazardous_conditions for x in ["Thunderstorm", "wind", "winds"]) else "MEDIUM"
        return WeatherAnalysis(
            hazardous_conditions=hazardous_conditions,
            weather_summary="[DEMO MODE] Weather hazards detected: " + "; ".join(hazardous_conditions),
            impact_level=impact_level
        )

    return WeatherAnalysis(
        hazardous_conditions=[],
        weather_summary="[DEMO MODE] Clear weather, light winds.",
        impact_level="LOW"
    )

@node(name="briefing_generator")
def mock_briefing_generator(node_input: str) -> FlightBriefing:
    """Mock briefing generator for DEMO_MODE."""
    payload = json.loads(node_input)
    flight = payload.get("flight_details", {})
    risk = payload.get("risk_assessment", {})
    notam_sum = payload.get("notam_summary", "")
    weather_sum = payload.get("weather_summary", "")
    review = payload.get("human_review")
    
    flight_number = flight.get("flight_number", "UNKNOWN")
    origin = flight.get("origin_airport", "UNKNOWN")
    destination = flight.get("destination_airport", "UNKNOWN")
    action = risk.get("recommended_action", "PROCEED")
    score = risk.get("risk_score", 0)
    level = risk.get("risk_level", "LOW")
    
    # Check if security warning was flagged
    is_injection = "SECURITY ALERT" in str(risk.get("detected_risks", []))
    
    if is_injection:
        return FlightBriefing(
            operational_summary=f"[DEMO MODE] {flight_number} - Security event detected",
            detected_risks=["Prompt injection detected", "Unsafe user instructions blocked"],
            risk_score=score,
            risk_level=level,
            recommended_action=action,
            final_briefing_text=(
                f"[DEMO MODE] Flight Crew Operational Briefing for {flight_number} from {origin} to {destination}.\n"
                f"Operational Status: {action}\n\n"
                f"--- Security Review ---\n"
                f"Prompt injection attempt detected.\n"
                f"Unsafe user instructions were blocked before downstream NOTAM and weather analysis.\n\n"
                f"--- Risk Metrics ---\n"
                f"Risk Score: {score}/100\n"
                f"Risk Level: {level}\n\n"
                f"--- Human Review Output ---\n"
                f"Status: Approved with override\n"
                f"Reviewer Comments: APPROVE\n"
            ),
            human_reviewed=True,
            reviewer_comments="Security case reviewed"
        )
        
    hr_status = "Approved"
    comments = None
    if review:
        hr_status = "Approved with override" if review.get("approved") else "Rejected"
        comments = review.get("reviewer_comments")
        
    final_briefing_text = (
        f"[DEMO MODE] Flight Crew Operational Briefing for {flight_number} from {origin} to {destination}.\n"
        f"Scheduled Time: {flight.get('scheduled_time', 'N/A')}\n"
        f"Operational Status: {action}\n\n"
        f"--- Hazard Summaries ---\n"
        f"NOTAMs: {notam_sum}\n"
        f"Weather: {weather_sum}\n\n"
        f"--- Risk Metrics ---\n"
        f"Risk Score: {score}/100\n"
        f"Risk Level: {level}\n"
    )
    if review:
        final_briefing_text += f"\n--- Human Review Output ---\nStatus: {hr_status}\nReviewer Comments: {comments or 'None'}\n"
        
    return FlightBriefing(
        operational_summary=f"[DEMO MODE] {flight_number} - {action}",
        detected_risks=risk.get("detected_risks", []),
        risk_score=score,
        risk_level=level,
        recommended_action=action,
        final_briefing_text=final_briefing_text,
        human_reviewed=bool(review),
        reviewer_comments=comments
    )

# Dynamic node selection based on DEMO_MODE config
active_notam_analyst = mock_notam_analyst if DEMO_MODE else notam_analyst
active_weather_analyst = mock_weather_analyst if DEMO_MODE else weather_analyst
active_briefing_generator = mock_briefing_generator if DEMO_MODE else briefing_generator

@node
def handle_security_block(ctx: Context, node_input: FlightOpsRequest) -> Event:
    """Short-circuit risk assessment for security events."""
    assessment = RiskAssessment(
        detected_risks=["SECURITY ALERT: Prompt injection attempt detected"],
        risk_score=100,
        risk_level="HIGH",
        recommended_action="HOLD",
        needs_human_review=True
    )
    # Save the assessment in state
    ctx.state["risk_assessment"] = assessment.model_dump()
    ctx.state["notam_summary"] = "[SECURITY SHIELD ACTIVE] NOTAM analysis bypassed."
    ctx.state["weather_summary"] = "[SECURITY SHIELD ACTIVE] Weather analysis bypassed."
    
    return Event(output=assessment)

# =====================================================================
# 7. Workflow Definition
# =====================================================================

edges = [
    # A. Validate & Secure
    ('START', validate_input),
    
    # B. Routing validation outcome
    (validate_input, {
        "invalid": validation_failure, 
        "security_flag": handle_security_block,
        "valid": (active_notam_analyst, active_weather_analyst)
    }),
    
    # C. Join parallel analysis results
    ((active_notam_analyst, active_weather_analyst), join_analyses),
    
    # D. Deterministic risk calculation
    (join_analyses, assess_risk),
    
    # E. Check if human review is needed
    (assess_risk, route_risk),
    
    # F. Routing from risk check
    (route_risk, {"human_review": human_review, "direct_briefing": prepare_briefing_prompt}),
    
    # G. Security block path routes directly to human review
    (handle_security_block, human_review),
    
    # H. After human review, prepare the briefing prompt
    (human_review, prepare_briefing_prompt),
    
    # I. Generate final briefing
    (prepare_briefing_prompt, active_briefing_generator)
]

root_agent = Workflow(
    name="aeroops_ai_workflow",
    edges=edges,
    description="Multi-agent flight operations assistant that coordinates validation, hazard analysis, risk scoring, and human review."
)

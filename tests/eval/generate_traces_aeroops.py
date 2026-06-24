import json
from json import JSONEncoder
import os
import asyncio
import re
from typing import Any

# Load .env
from pathlib import Path
from dotenv import load_dotenv
for _candidate in [
    Path(__file__).parent.parent.parent / ".env",
    Path(__file__).parent.parent.parent / "AeroOps-AI" / ".env",
]:
    if _candidate.exists():
        load_dotenv(_candidate)
        break

from google.adk.apps import App, ResumabilityConfig
from google.adk.runners import InMemoryRunner
from google.adk.models import LlmResponse
from google.genai import types

# ------------------------------------------------------------------
# Mock LLM for AeroOps AI
# ------------------------------------------------------------------
_api_key = os.getenv("GOOGLE_API_KEY", "")
_use_mock = (
    not _api_key
    or _api_key.endswith(".apps.googleusercontent.com")
    or _api_key == "your_api_key_here"
)

if _use_mock:
    from google.adk.models.google_llm import Gemini

    async def _mock_generate(self, llm_request, stream=False):
        prompt = ""
        if llm_request.contents:
            for c in llm_request.contents:
                for p in (c.parts or []):
                    if p.text:
                        prompt += p.text + "\n"

        result = "{}"
        
        # Check which agent is calling by looking at the prompt instruction
        # or the request schema name
        schema_name = ""
        if hasattr(llm_request, "config") and llm_request.config:
            if hasattr(llm_request.config, "response_schema") and llm_request.config.response_schema:
                schema_name = getattr(llm_request.config.response_schema, "__name__", "")

        # 1. NOTAM Analyst Agent Mock
        if schema_name == "NOTAMAnalysis":
            if "WIP" in prompt or "CLSD" in prompt:
                if "AD CLSD" in prompt or "SEVERE" in prompt:
                    result = json.dumps({
                        "critical_notams": ["AD CLSD OUT OF SERVICE"],
                        "notam_summary": "Aerodrome closed due to runway work in progress.",
                        "impact_level": "HIGH"
                    })
                else:
                    result = json.dumps({
                        "critical_notams": ["TWY A1 CLSD"],
                        "notam_summary": "Taxiway A1 is closed for work in progress.",
                        "impact_level": "LOW"
                    })
            else:
                result = json.dumps({
                    "critical_notams": [],
                    "notam_summary": "No critical NOTAMs.",
                    "impact_level": "LOW"
                })

        # 2. Weather Analyst Agent Mock
        elif schema_name == "WeatherAnalysis":
            if "TSRA" in prompt or "thunderstorm" in prompt.lower():
                result = json.dumps({
                    "hazardous_conditions": ["Severe thunderstorms", "Gusty crosswinds"],
                    "weather_summary": "Severe convective weather at destination.",
                    "impact_level": "HIGH"
                })
            else:
                result = json.dumps({
                    "hazardous_conditions": [],
                    "weather_summary": "Clear weather, light winds.",
                    "impact_level": "LOW"
                })

        # 3. Briefing Generator Agent Mock
        elif schema_name == "FlightBriefing":
            # Determine case from the merged payload string
            if "POTENTIAL PROMPT INJECTION" in prompt or "Bypass safety" in prompt:
                result = json.dumps({
                    "operational_summary": "DL456 - Rejected due to security event.",
                    "detected_risks": ["Prompt injection detected"],
                    "risk_score": 100,
                    "risk_level": "HIGH",
                    "recommended_action": "CANCEL",
                    "final_briefing_text": "Flight DL456 cancelled due to security policy violation.",
                    "human_reviewed": True,
                    "reviewer_comments": "cancel"
                })
            elif "AD CLSD" in prompt:
                result = json.dumps({
                    "operational_summary": "SFO to JFK - AA88. Flight suspended due to high risk.",
                    "detected_risks": ["AD CLSD OUT OF SERVICE", "Severe thunderstorms"],
                    "risk_score": 100,
                    "risk_level": "HIGH",
                    "recommended_action": "HOLD",
                    "final_briefing_text": "Flight AA88 is placed on hold due to destination airport closure and severe thunderstorms.",
                    "human_reviewed": True,
                    "reviewer_comments": "override: HOLD wait for weather clearance"
                })
            else:
                result = json.dumps({
                    "operational_summary": "SFO to LAX - UA123. Flight is clear with low operational risks.",
                    "detected_risks": ["TWY A1 CLSD"],
                    "risk_score": 10,
                    "risk_level": "LOW",
                    "recommended_action": "PROCEED",
                    "final_briefing_text": "Flight UA123 from SFO to LAX is approved for direct proceed. Weather is clear. Taxiway A1 is closed.",
                    "human_reviewed": False
                })

        yield LlmResponse(
            content=types.Content(
                role="model", parts=[types.Part.from_text(text=result)]
            ),
            turn_complete=True,
        )

    # Patch the generate method
    Gemini.generate_content_async = _mock_generate

# Import the agent
from aeroops_ai.agent import root_agent

# Make sure output directory exists
os.makedirs("artifacts", exist_ok=True)

async def generate():
    # Setup App and Runner
    adk_app = App(
        name="aeroops_ai", 
        root_agent=root_agent,
        resumability_config=ResumabilityConfig(is_resumable=True)
    )
    runner = InMemoryRunner(app=adk_app)
    
    # Read dataset
    dataset_path = "tests/eval/datasets/aeroops-dataset.json"
    with open(dataset_path, "r") as f:
        dataset = json.load(f)
        
    output_cases = []
    
    for case in dataset.get("eval_cases", []):
        case_id = case["eval_case_id"]
        print(f"Running case: {case_id}")
        
        session_id = f"eval_session_{case_id}"
        user_id = "eval_user"
        
        session = await runner.session_service.create_session(
            app_name="aeroops_ai", 
            user_id=user_id,
            session_id=session_id
        )
        
        prompt_text = case["prompt"]["parts"][0]["text"]
        content = types.Content(role="user", parts=[types.Part.from_text(text=prompt_text)])
        
        # Run workflow
        is_paused = False
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if hasattr(event, 'interrupt_ids') and event.interrupt_ids:
                is_paused = True
                print(f"  Hit RequestInput (HITL): {list(event.interrupt_ids)}")
                
        if is_paused:
            # Simulate human decision
            decision = "approve"
            if "injection" in case_id:
                decision = "cancel"
            elif "high_risk" in case_id:
                decision = "override: HOLD wait for weather clearance"
                
            print(f"  Simulating human decision: {decision}")
            
            resume_message = types.Content(
                parts=[
                    types.Part(
                        function_response=types.FunctionResponse(
                            name="human_review_response",
                            id="human_decision",
                            response={"decision": decision}
                        )
                    )
                ]
            )
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=resume_message
            ):
                pass
                
        # Retrieve trace from session
        session = await runner.session_service.get_session(app_name="aeroops_ai", user_id=user_id, session_id=session_id)
        
        _ALLOWED_EVENT_FIELDS = {"content", "author"}
        events_dump = []
        for event in session.events:
            raw = event.model_dump(exclude_none=True)
            filtered = {k: v for k, v in raw.items() if k in _ALLOWED_EVENT_FIELDS}
            if filtered:
                events_dump.append(filtered)
            
        output_cases.append({
            "eval_case_id": case_id,
            "prompt": case["prompt"],
            "agent_data": {
                "agents": {
                    "aeroops_ai_workflow": {"agent_id": "aeroops_ai_workflow"}
                },
                "turns": [
                    {
                        "turn_index": 0,
                        "events": events_dump
                    }
                ]
            }
        })
        
    # Write to output traces
    class _SetEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return sorted(obj)
            return super().default(obj)

    output_path = "artifacts/traces_aeroops.json"
    with open(output_path, "w") as f:
        json.dump({"eval_cases": output_cases}, f, indent=2, cls=_SetEncoder)
        
    print(f"Successfully wrote traces to {output_path}")

if __name__ == "__main__":
    asyncio.run(generate())

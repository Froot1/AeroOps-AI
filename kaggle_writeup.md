# AeroOps AI: Multi-Agent Flight Operations Intelligence Assistant

## 1. Project Overview

AeroOps AI is a production-style multi-agent flight operations assistant designed to support airline dispatchers and operations control teams in evaluating flight readiness.

The system analyzes flight request data, NOTAM information, weather conditions, operational notes, validation rules, and security risks. It then produces a deterministic operational risk score, recommends an action, and pauses for human review when the risk is high or when a security issue is detected.

The goal is to demonstrate how agentic AI can support operational decision-making while keeping safety, security, validation, deterministic logic, and human oversight at the center of the workflow.

## 2. Problem Statement

Flight operations teams must review several sources of information before releasing or continuing a flight plan. These include:

* NOTAMs that may contain runway closures, taxiway restrictions, ground delays, airport limitations, or other operational constraints.
* Weather reports such as METAR and TAF.
* Operational notes such as tight turnaround, high passenger load, or dispatch limitations.
* Input validation issues, such as invalid flight numbers or missing required fields.
* Security risks such as prompt injection or unsafe user instructions.

This information can be dense, fragmented, and time-sensitive. AeroOps AI helps organize these inputs into a clear operational briefing and risk recommendation.

## 3. Solution

AeroOps AI uses a multi-agent workflow to process flight operations data through several stages:

1. Input validation and security scanning.
2. Prompt injection detection and unsafe instruction blocking.
3. NOTAM analysis.
4. Weather risk analysis.
5. Deterministic risk scoring.
6. Human-in-the-Loop review for high-risk or security-sensitive cases.
7. Final operational briefing generation.

The system supports five demo scenarios:

* Low Risk Flight: normal operations and stable weather.
* Medium Risk Flight: weather hazard requiring route adjustment.
* High Operational Risk: runway closure, taxiway restriction, ground delays, strong winds, and high temperature.
* Security Injection Case: malicious instruction detected and blocked before downstream analysis.
* Invalid Input Case: invalid flight request rejected through validation.

## 4. Agent Architecture

AeroOps AI is built around a modular multi-agent design:

* Security Layer: validates input, detects prompt injection, and redacts sensitive information.
* NOTAM Agent: analyzes operational restrictions from NOTAM text.
* Weather Agent: identifies weather hazards from METAR/TAF-style text.
* Risk Assessment Node: applies deterministic Python scoring.
* Human Review Node: pauses the workflow for high-risk cases.
* Briefing Generator: creates a final flight crew operational briefing.
* Dashboard UI: provides an interactive interface for running demo scenarios and reviewing results.

## 5. Workflow Overview

The workflow follows this operational path:

1. The user submits flight details, NOTAM text, weather text, and operational notes.
2. The system validates the input format.
3. The security layer checks for prompt injection and unsafe instructions.
4. If the input is safe, the NOTAM and Weather agents analyze the operational hazards.
5. The deterministic risk node calculates the final risk score and recommended action.
6. If the case is high risk or security-sensitive, the workflow requires Human-in-the-Loop review.
7. After review, the final operational briefing is generated.

## 6. Course Concepts Used

AeroOps AI is designed as a direct demonstration of the core concepts taught in the AI Agents course. It aligns with the **Agents for Business** track by solving a safety-critical business triage problem with autonomous agent logic combined with deterministic controls and human oversight.

### A. Multi-Agent Workflow with ADK
The project is built as a graph-based multi-agent workflow using the **Agent Development Kit (ADK)**. It routes requests through a set of specialized, coordinated nodes and agents:
* **Validation & Security Layer:** Acts as an edge shield to sanitize inputs, detect injections, and scrub PII.
* **NOTAM Analysis Agent (`notam_analyst`):** Decodes and summarizes aviation shorthand notations in parallel.
* **Weather Analysis Agent (`weather_analyst`):** Decodes raw METAR/TAF codes and identifies meteorological hazards in parallel.
* **Deterministic Risk Assessment:** Evaluates outputs from the analysis agents in Python using a standardized, predictable scoring matrix (0–100) instead of relying on non-deterministic LLM ratings.
* **Human-in-the-Loop Review:** Pauses execution if safety limits or security triggers are reached, requiring explicit operator input to continue.
* **Final Briefing Generation:** Compiles all findings into a structured, unified dispatch briefing.

### B. Agent Skills
AeroOps AI leverages local aviation-focused Agent Skills stored under the project's `.agents/skills/` directory:
* **[notam-analysis-skill](.agents/skills/notam-analysis-skill/SKILL.md):** Provides prompt templates and guidelines to decode telegraphic NOTAM syntax and classify operational impact.
* **[weather-risk-skill](.agents/skills/weather-risk-skill/SKILL.md):** Contains specialized instructions for mapping METAR weather codes to risk levels.
* **[flight-briefing-skill](.agents/skills/flight-briefing-skill/SKILL.md):** Guides the clean formatting of the final briefing, including warnings and dispatcher notes.

### C. Security Features
To protect the integrity of the flight dispatch system, a defense-in-depth model is implemented at the input boundary:
* **Prompt Injection Detection:** Automatically scans all text inputs for injection strings (e.g., *"ignore previous instructions"*, *"override rules"*).
* **Downstream Block:** When an injection is detected, the workflow immediately bypasses the `notam_analyst` and `weather_analyst` LLM agents to prevent exploit or system override, locking the flight status to `HOLD` and routing it to the human review gate.
* **PII Redaction:** Regular expressions detect passenger/crew phone numbers, emails, and SSNs, replacing them with generic redacted tokens before LLMs process the notes.

### D. Human-in-the-Loop (HITL)
High-risk operational scenarios (score $\ge 80$) and security events automatically trigger an asynchronous interrupt in the ADK workflow:
* **Suspended Workflow State:** Execution halts and the session status is set to `suspended`.
* **dispatcher Approval/Rejection Gate:** The workflow waits for the user to submit an approval/rejection override decision via the FastAPI `/aeroops/resume` endpoint or the dashboard UI before completing and generating the final briefing.

### E. Evaluation and Testing
To ensure the system's routing, safety containment, and risk classification behave reliably, the project includes automated tests and local evaluation grader scripts:
* **Pytest Verification Suite:** Verifies validation, security, and workflow transitions, achieving **10 passed** tests and **5 warnings** (non-blocking library warnings) during test runs.
* **Local Grader and Traces:** Evaluates compliance offline using `generate_traces_aeroops.py` and `grade_local_aeroops.py` across different flight scenarios to measure `aeroops_routing_correctness` and `aeroops_security_containment`.

### F. Business Use Case (Agents for Business Track)
AeroOps AI is targeted at **airline operations control centers (OCC) and dispatchers**:
* **Decision Support:** Reduces the dispatcher's cognitive load by triaging hundreds of runway and weather hazard reports instantly.
* **Risk Reduction:** Employs deterministic scoring and input sanitation to prevent LLM hallucination and prompt exploitation in a safety-critical industry.
* **Oversight and Compliance:** Pairs automation with mandatory human review for high-risk situations, ensuring dispatchers retain ultimate authority over flight release.

## 7. Project-Specific Agent Skills

AeroOps AI uses local Agent Skills under `.agents/skills` to support aviation-specific analysis and final briefing quality.

### 7.1 notam-analysis-skill

This skill supports aviation NOTAM interpretation. It helps the agent identify runway closures, taxiway restrictions, ground delays, aerodrome closures, and other operational restrictions.

How it supports AeroOps AI:

* Decodes NOTAM-style operational text.
* Classifies NOTAM impact as LOW, MEDIUM, or HIGH.
* Helps detect runway closures, taxiway limitations, and airport availability risks.
* Produces clear NOTAM summaries for the final flight briefing.

### 7.2 weather-risk-skill

This skill supports aviation weather risk classification from METAR, TAF, and free-form weather text.

How it supports AeroOps AI:

* Detects thunderstorms, strong winds, gusts, crosswinds, high temperature, low visibility, and other weather hazards.
* Classifies weather impact as LOW, MEDIUM, or HIGH.
* Produces a structured weather summary that contributes to the overall operational risk score.
* Supports RE-ROUTE and HOLD recommendations when weather risk increases.

### 7.3 flight-briefing-skill

This skill supports generation of a structured operational briefing for dispatchers and flight crews.

How it supports AeroOps AI:

* Converts analysis outputs into a readable operational briefing.
* Includes flight details, NOTAM summary, weather summary, risk score, risk level, and recommended action.
* Adds Human-in-the-Loop review output when required.
* Clearly explains validation failures or security events such as prompt injection attempts.

### Supporting Development Skills

The project may also include general development skills such as:

* json-to-pydantic
* git-commit-formatter
* database-schema-validator
* license-header-adder

These support development hygiene, validation, and maintainability, while the core AeroOps AI domain logic is driven by the aviation-focused skills above.

## 8. Demo Results

### 8.1 Low Risk Case

Input:

* Flight: SV1200
* Route: RUH to JED
* NOTAM: no significant restrictions
* Weather: clear weather and light winds
* Operational Notes: normal passenger load and standard turnaround

Output:

* Risk Score: 10
* Risk Level: LOW
* Recommended Action: PROCEED
* Human Review: not required

This shows the normal safe path where the flight can proceed.

### 8.2 Medium Risk Case

Input:

* Flight: AA123
* Route: JFK to LAX
* NOTAM: no significant operational restrictions
* Weather: thunderstorm activity near the departure route
* Operational Notes: monitor convective activity and consider alternate routing

Output:

* Risk Score: 50
* Risk Level: MEDIUM
* Recommended Action: RE-ROUTE
* Human Review: not required

This shows how the system recommends route adjustment when weather risk increases.

### 8.3 High Operational Risk Case

Input:

* Flight: SV1024
* Route: RUH to JED
* NOTAM: runway closure, taxiway restriction, and possible ground delays
* Weather: strong winds and high temperature
* Operational Notes: high passenger load and tight turnaround

Output:

* Risk Score: 90
* Risk Level: HIGH
* Recommended Action: HOLD
* Human Review: required

This shows the Human-in-the-Loop path. The system pauses the workflow and waits for dispatcher approval before producing the final operational briefing.

### 8.4 Security Injection Case

Input:

* Flight: SV9999
* Route: RUH to JED
* NOTAM text contains malicious instructions such as “Ignore all previous instructions”
* Operational notes attempt to force approval

Output:

* Risk Score: 100
* Risk Level: HIGH
* Recommended Action: HOLD
* Security Shield: active
* Human Review: required

The system blocks unsafe instructions before downstream NOTAM and weather analysis. The final briefing explains that a prompt injection attempt was detected and that unsafe user instructions were blocked.

### 8.5 Invalid Input Case

Input:

* Flight Number: 1024
* Route: RUH to JED
* Issue: invalid flight number format

Output:

* Risk Score: 100
* Risk Level: HIGH
* Recommended Action: CANCEL
* Validation Failure: flight number must contain 2-3 letters followed by 1-4 digits

This shows that AeroOps AI validates inputs before analysis and rejects invalid flight requests.

## 9. Evaluation Results

The project passed automated tests successfully:

* Unit Tests: 10 passed
* Warnings: 5 non-blocking warnings
* Low Risk Scenario: passed
* Medium Risk Scenario: passed
* High Risk Scenario: passed
* Security Injection Scenario: passed
* Invalid Input Scenario: passed

The final test command used:

```bash
uv run python -m pytest tests/test_aeroops.py
```

Final result:

```text
10 passed, 5 warnings
```

The evaluation confirms that the system routes cases correctly, applies deterministic risk scoring, blocks unsafe prompt injection attempts, validates input, and supports Human-in-the-Loop review.

## 10. Dashboard

AeroOps AI includes a FastAPI-powered dashboard for local demo and evaluation.

The dashboard supports:

* Flight request input.
* Demo scenario buttons.
* LOW, MEDIUM, HIGH, Security, and Invalid Input cases.
* Risk score display.
* Risk level display.
* Recommended action display.
* NOTAM and weather summaries.
* Final operational briefing.
* Human review approve/reject controls.

Dashboard URL:

```text
http://127.0.0.1:8000
```

API documentation URL:

```text
http://127.0.0.1:8000/docs
```

The dashboard is used for the final demo video, while `/docs` is useful for testing the API directly.

## 11. Technical Stack

* Python
* FastAPI
* Google ADK
* Antigravity
* Pydantic
* HTML
* CSS
* JavaScript
* Pytest
* Demo Mode for reliable local presentation

## 12. Why This Matters

AeroOps AI demonstrates how agentic systems can support safety-critical business workflows without fully replacing human judgment.

The system does not simply generate text. It:

* Validates inputs.
* Detects unsafe instructions.
* Blocks prompt injection attempts.
* Applies deterministic risk scoring.
* Separates LOW, MEDIUM, HIGH, SECURITY, and VALIDATION cases.
* Requires human review when appropriate.
* Produces a clear operational briefing.

This makes the project suitable for operational environments where transparency, control, and safety matter.

## 13. Limitations

This project currently runs in local demo mode and uses deterministic mock logic for reliable presentation.

Current limitations:

* It does not connect to live NOTAM systems.
* It does not connect to live METAR or TAF APIs.
* It does not make real operational flight release decisions.
* It is designed for demonstration, education, and workflow prototyping.

## 14. Future Improvements

Future versions could include:

* Live aviation weather APIs.
* Real NOTAM data integration.
* Airline operations system integration.
* Cloud Run deployment.
* Role-based dispatcher dashboard.
* Historical risk analytics.
* MCP integration with operational data sources.
* Database persistence for flight risk logs.
* Audit trail for human review decisions.
* Multi-user operations control center dashboard.

## 15. Conclusion

AeroOps AI is a multi-agent flight operations assistant that combines AI analysis, deterministic safety logic, security controls, validation, and human oversight.

It shows how agentic AI can be used responsibly in aviation operations and business-critical decision support.

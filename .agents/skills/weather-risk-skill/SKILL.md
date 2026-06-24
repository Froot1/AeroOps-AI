---
name: weather-risk-skill
description: Assess weather conditions and assign operational risk levels for flight planning.
---

# Weather Risk Skill

This skill evaluates the meteorological data supplied for a flight (e.g., METAR, TAF, free‑text weather notes) and translates it into a **risk classification** (LOW, MEDIUM, HIGH) that can be used by the AeroOps AI workflow.

## Input Expected
- `weather_text`: Raw weather report string (METAR/TAF or free‑form description).
- Optional: `scheduled_time` (ISO‑8601) to consider time‑dependent phenomena (e.g., forecasts).

## Risk Assessment Rules
| Condition | Risk Level |
|-----------|------------|
| **HIGH**  | • Visibility < 1000 m OR < 3 SM in IFR conditions
|            | • Wind shear, thunderstorms, severe turbulence, or lightning in the vicinity
|            | • Significant icing conditions (temperature ≤ 0 °C with visible moisture) 
|            | • Runway surface contamination (snow/ice) with reduced braking performance
| **MEDIUM**| • Moderate turbulence, light rain/sleet, visibility 1000‑3000 m
|            | • Winds > 30 kt or cross‑winds exceeding runway limits
|            | • Cloud ceiling 500‑1500 ft (IFR) but no severe weather
| **LOW**   | • VMC/clear weather, visibility > 5 km, light winds (< 15 kt)
|            | • No significant hazards reported

## Output Produced
- `weather_risk_level`: *LOW*, *MEDIUM* or *HIGH*.
- `weather_summary`: Human‑readable narrative explaining the assessment.

## Usage in Agent
The AeroOps AI agent can call this skill to obtain `weather_risk_level` and embed the summary in the final briefing, or to trigger a **Human‑in‑the‑Loop** review when risk is HIGH.

---

**Implementation notes**
- The skill should be pure logic; no external API calls.
- Accept both structured METAR strings and free‑form text using simple keyword detection.
- Return JSON‑compatible fields as shown in the output section.

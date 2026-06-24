---
name: notam-analysis-skill
description: Guidelines and dictionaries for decoding and analyzing aviation NOTAMs (Notice to Air Missions).
---

# NOTAM Analysis Skill

This skill assists the NOTAM Analysis Agent in translating and assessing the impact of aviation NOTAMs (Notice to Air Missions). NOTAMs are typically written in uppercase, abbreviated telegram-style text, which can be obscure.

## Common NOTAM Abbreviations

| Abbreviation | Expanded Form | Operational Significance |
|--------------|---------------|--------------------------|
| **AD**       | Aerodrome     | Entire airport           |
| **RWY**      | Runway        | Landing/takeoff strip    |
| **TWY**      | Taxiway       | Ground movement routing  |
| **CLSD**     | Closed        | Out of service / blocked |
| **U/S**      | Unserviceable | Equipment broken/failed  |
| **LGT**      | Lighting      | Visual aids unserviceable|
| **OPR**      | Operating     | Current state            |
| **WIP**      | Work In Progress| Construction/maintenance|
| **OBST**     | Obstruction   | Crane, tower, or hazard  |
| **ILS**      | Instrument Landing System | Precision approach system |

## Severity and Criticality Assessment

When evaluating NOTAM impact on a flight request:

1. **CRITICAL / HIGH Risk:**
   - `AD CLSD` (Aerodrome closed) at origin, destination, or selected alternate.
   - Primary runway closed (e.g. `RWY 10R/28L CLSD`) with no suitable alternatives.
   - Critical precision approach systems unserviceable (`ILS GP U/S` - Glide Path unserviceable) during low-visibility conditions.

2. **MEDIUM Risk:**
   - Secondary runway closures.
   - Major taxiway closures (`TWY A CLSD`) causing significant taxi delays.
   - Work in progress on or near runways (`WIP RY 09/27`).
   - Partial airport capacity constraints (e.g. noise curfews, custom hours).

3. **LOW Risk:**
   - Minor taxiway or ramp closures.
   - Obstruction lights unserviceable (`OBST LGT U/S`) unless in critical low-altitude approach corridors.
   - General information bulletins (e.g. birds in vicinity).

## Instructions for the Agent

1. **Decode the NOTAM**: Translate all uppercase abbreviations in the raw text into clear, readable English.
2. **Determine Runway/Facility Status**: Identify which specific assets (runways, taxiways, ILS) are affected.
3. **Assess Operational Impact**: Classify the risk (LOW, MEDIUM, HIGH) by mapping the affected assets against the scheduled flight time and scheduled airports.

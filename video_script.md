# AeroOps AI Final Demo Script

## Introduction

Hello, this is AeroOps AI, a multi-agent flight operations intelligence assistant.

The system helps flight operations teams analyze flight readiness using NOTAMs, weather information, operational notes, validation rules, security checks, deterministic risk scoring, and human review.

## Dashboard Overview

This is the AeroOps AI dashboard.
It includes five demo scenarios:

LOW Risk Demo
MEDIUM Risk Demo
HIGH Risk Demo
Security Injection Demo
Invalid Input Demo

Each scenario fills the form automatically, and then I click Run Analysis to execute the workflow.

## LOW Risk Demo

First, I will run the LOW Risk scenario.

The flight is SV1200 from RUH to JED.
There are no major NOTAM restrictions and the weather is stable.

The result is:

Risk Score: 10
Risk Level: LOW
Recommended Action: PROCEED

This means the flight can continue without human review.

## MEDIUM Risk Demo

Next, I will run the MEDIUM Risk scenario.

This case includes thunderstorm activity near the route.

The result is:

Risk Score: 50
Risk Level: MEDIUM
Recommended Action: RE-ROUTE

This shows that the system recommends adjusting the route due to weather risk.

## HIGH Operational Risk Demo

Now I will run the HIGH Risk scenario.

This case includes a runway closure, taxiway restriction, possible ground delays, strong winds, and high temperature.

The result is:

Risk Score: 80
Risk Level: HIGH
Recommended Action: HOLD

Because this is a high-risk case, the system requires Human-in-the-Loop review.

After approval, the system generates the final operational briefing.

## Security Injection Demo

Next, I will test the security layer.

This input contains a prompt injection attempt asking the system to ignore previous instructions and mark the flight as safe.

AeroOps AI detects the unsafe instruction and activates the Security Shield.

The result is:

Risk Score: 100
Risk Level: HIGH
Recommended Action: HOLD

The NOTAM and weather analysis are bypassed because the input is unsafe.

After human review, the system generates a security-focused final briefing.

## Invalid Input Demo

Finally, I will test input validation.

This case uses an invalid flight number format: 1024.

The system rejects the request and returns:

Risk Score: 100
Risk Level: HIGH
Recommended Action: CANCEL

The final briefing explains that the flight number must contain two or three letters followed by one to four digits.

## Testing

The project also includes automated tests.

The final test result shows:

10 tests passed.

This confirms that the main workflow, validation, risk scoring, and security behavior are working correctly.

## Conclusion

AeroOps AI demonstrates how agentic AI can support aviation operations while keeping safety, validation, security, deterministic scoring, and human oversight at the center.

Thank you.

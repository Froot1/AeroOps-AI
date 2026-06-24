import os
from dotenv import load_dotenv

load_dotenv()

# Model configuration
MODEL_NAME = os.getenv("AEROOPS_MODEL_NAME", "gemini-2.5-flash")
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Risk configuration
HIGH_RISK_THRESHOLD = 80  # Risk score >= 80 triggers human-in-the-loop review
MEDIUM_RISK_THRESHOLD = 35 # Risk score >= 35 is MEDIUM, below is LOW

import re
from datetime import datetime

# Regex patterns for validation
AIRPORT_CODE_PATTERN = re.compile(r"^[A-Z0-9]{3,4}$", re.IGNORECASE)
FLIGHT_NUMBER_PATTERN = re.compile(r"^[A-Z]{2,3}\d{1,4}$", re.IGNORECASE)

# Regex patterns for PI Redaction
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d[ -]*?){13,16}\b")

# Prompt injection keywords to flag
PROMPT_INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore previous", 
    "force system",
    "approve this flight",
    "mark this flight as safe",
    "override instructions",
    "bypass safety",
    "system prompt", 
    "override safety", 
    "disregard rules",
    "you are now a", 
    "new instructions",
    "developer mode",
    "ignore rules",
    "bypass security"
]

def validate_flight_request(data: dict) -> list[str]:
    """Validates structure and content of a flight operations request."""
    errors = []
    
    # Check required fields
    required_fields = ["origin_airport", "destination_airport", "flight_number", "scheduled_time"]
    for field in required_fields:
        if not data.get(field):
            errors.append(f"Missing required field: '{field}'")
            
    # Validate origin airport code
    origin = data.get("origin_airport", "")
    if origin and not AIRPORT_CODE_PATTERN.match(origin):
        errors.append(f"Invalid origin airport code: '{origin}'. Must be a 3-4 letter IATA/ICAO code.")
        
    # Validate destination airport code
    dest = data.get("destination_airport", "")
    if dest and not AIRPORT_CODE_PATTERN.match(dest):
        errors.append(f"Invalid destination airport code: '{dest}'. Must be a 3-4 letter IATA/ICAO code.")
        
    # Validate flight number
    flight_num = data.get("flight_number", "")
    if flight_num and not FLIGHT_NUMBER_PATTERN.match(flight_num):
        errors.append(f"Invalid flight number format: '{flight_num}'. Must be 2-3 letters followed by 1-4 digits (e.g. AA123).")
        
    # Validate scheduled time format (ISO datetime check)
    sched_time = data.get("scheduled_time", "")
    if sched_time:
        # Strip trailing Z for easy parsing
        time_str = sched_time[:-1] if sched_time.endswith("Z") else sched_time
        try:
            datetime.fromisoformat(time_str)
        except ValueError:
            errors.append(f"Invalid scheduled time format: '{sched_time}'. Must be in ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ).")
            
    return errors

def detect_prompt_injection(text: str) -> bool:
    """Scans text for common prompt injection/override phrases."""
    if not text:
        return False
    
    text_lower = text.lower()
    for kw in PROMPT_INJECTION_KEYWORDS:
        if kw in text_lower:
            return True
    return False

def redact_sensitive_pi(text: str) -> tuple[str, list[str]]:
    """Redacts emails, phone numbers, SSNs, and credit cards from the text."""
    if not text:
        return "", []
    
    redacted_categories = []
    
    # Redact Emails
    if EMAIL_PATTERN.search(text):
        text = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
        redacted_categories.append("Email")
        
    # Redact Phone Numbers
    if PHONE_PATTERN.search(text):
        text = PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
        redacted_categories.append("Phone")
        
    # Redact SSNs
    if SSN_PATTERN.search(text):
        text = SSN_PATTERN.sub("[REDACTED_SSN]", text)
        redacted_categories.append("SSN")
        
    # Redact Credit Cards
    if CREDIT_CARD_PATTERN.search(text):
        text = CREDIT_CARD_PATTERN.sub("[REDACTED_CC]", text)
        redacted_categories.append("CreditCard")
        
    return text, redacted_categories

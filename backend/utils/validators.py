#input validate email,cgpa,etc fields
import re
from typing import List, Tuple, Optional

#regex code email : line 5 to 8 wrote using help of llm
_EMAIL_RE = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)


def validate_email(email: str) -> bool: #validate email address
    if not email or not isinstance(email, str):
        return False
    return bool(_EMAIL_RE.match(email.strip()))


def validate_required(data: dict, fields: List[str]) -> Tuple[bool, Optional[str]]:#validate entered input not empty
    if data is None:
        return False, 'empty.'
    for field in fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ''):
            return False, f"'{field}' is required."
    return True, None


def validate_cgpa(cgpa) -> Tuple[bool, Optional[str]]:#cgpa within 10 
    try:
        cgpa = float(cgpa)
    except (TypeError, ValueError):
        return False, ' must be number'
    if cgpa < 0 or cgpa > 10:
        return False, 'must be bw 0 to 10'
    return True, None

"""
Validation and regex matching utilities.
"""
import re
from urllib.parse import urlparse
from typing import List, Any

def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(pattern, text)

def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text."""
    patterns = [
        r'\+?1?\d{9,15}',  # International format
        r'\(\d{3}\)\s?\d{3}-\d{4}',  # US format
        r'\d{3}-\d{3}-\d{4}',  # Standard format
    ]
    numbers = []
    for pattern in patterns:
        numbers.extend(re.findall(pattern, text))
    return list(set(numbers))

def extract_urls(text: str) -> List[str]:
    """Extract URLs from text."""
    pattern = r'https?://\S+'
    return re.findall(pattern, text)

def is_email_valid(email: str) -> bool:
    """Validate email address."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_url_valid(url: str) -> bool:
    """Validate URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_numeric(value: Any) -> bool:
    """Check if value is numeric."""
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False

def is_integer(value: Any) -> bool:
    """Check if value is integer."""
    try:
        int(value)
        return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
    except (TypeError, ValueError):
        return False

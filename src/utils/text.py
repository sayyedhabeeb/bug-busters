"""
Text and string manipulation utilities.
"""
import re
import string
from typing import List

def normalize_text(text: str, lowercase: bool = True, strip: bool = True) -> str:
    """
    Normalize text by removing extra spaces and optionally converting case.
    """
    if not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    if strip:
        text = text.strip()
    
    if lowercase:
        text = text.lower()
    
    return text

def slugify(text: str, separator: str = '-') -> str:
    """Convert text to URL-friendly slug."""
    text = normalize_text(text, lowercase=True)
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', separator, text)
    return text.strip(separator)

def camel_to_snake(text: str) -> str:
    """Convert camelCase to snake_case."""
    text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', text).lower()

def snake_to_camel(text: str) -> str:
    """Convert snake_case to camelCase."""
    components = text.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def remove_punctuation(text: str) -> str:
    """Remove punctuation from text."""
    return text.translate(str.maketrans('', '', string.punctuation))

def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text."""
    pattern = r'<[^>]+>'
    return re.sub(pattern, '', text)

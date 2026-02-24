"""
Hashing, dict, and list utilities.
"""
import hashlib
import uuid
from typing import Any, Dict, List, Optional

# --- Hash & UUID ---

def generate_hash(data: str, algorithm: str = 'sha256') -> str:
    """Generate hash of data."""
    if algorithm == 'md5':
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(data.encode()).hexdigest()
    return hashlib.sha256(data.encode()).hexdigest()

def generate_uuid(version: int = 4) -> str:
    """Generate UUID."""
    if version == 1:
        return str(uuid.uuid1())
    elif version == 3:
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, 'example.com'))
    elif version == 5:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, 'example.com'))
    return str(uuid.uuid4())

def generate_token(length: int = 32) -> str:
    """Generate random token."""
    return uuid.uuid4().hex[:length]

# --- Dict & List ---

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            items.append((new_key, len(v)))
        else:
            items.append((new_key, v))
    return dict(items)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def remove_duplicates(lst: List[Any], key: Optional[Any] = None) -> List[Any]:
    """Remove duplicates from list."""
    if key is None:
        seen = set()
        result = []
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    else:
        seen = set()
        result = []
        for item in lst:
            item_key = key(item) if callable(key) else item[key]
            if item_key not in seen:
                seen.add(item_key)
                result.append(item)
        return result

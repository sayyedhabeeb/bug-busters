"""
Date and time utilities.
"""
from datetime import datetime
from typing import Dict, Union

def to_datetime(value: Union[str, datetime]) -> datetime:
    """Convert value to datetime."""
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, str):
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
        ]
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return datetime.now()

def format_datetime(dt: datetime, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format datetime."""
    if isinstance(dt, datetime):
        return dt.strftime(fmt)
    return str(dt)

def get_time_diff(start: datetime, end: datetime = None) -> Dict[str, int]:
    """Calculate time difference."""
    if end is None:
        end = datetime.utcnow()
    
    diff = end - start
    total_seconds = int(diff.total_seconds())
    
    return {
        'days': total_seconds // 86400,
        'hours': (total_seconds % 86400) // 3600,
        'minutes': (total_seconds % 3600) // 60,
        'seconds': total_seconds % 60,
        'total_seconds': total_seconds
    }

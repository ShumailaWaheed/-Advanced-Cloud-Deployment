"""Shared utility functions for the todo chatbot application."""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import json
import hashlib
import re


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def get_current_iso_timestamp() -> str:
    """Get current time in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


def get_current_datetime() -> datetime:
    """Get current UTC datetime for database operations."""
    from datetime import timezone
    return datetime.now(timezone.utc)


def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_input(text: str) -> str:
    """Sanitize input text by removing potentially harmful characters."""
    if not text:
        return ""

    # Remove potentially harmful characters/sequences
    sanitized = text.strip()
    return sanitized


def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """Hash a string using the specified algorithm."""
    if algorithm == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hashing algorithm: {algorithm}")


def dict_to_json(data: Dict[str, Any]) -> str:
    """Convert dictionary to JSON string."""
    return json.dumps(data)


def json_to_dict(json_str: str) -> Dict[str, Any]:
    """Convert JSON string to dictionary."""
    return json.loads(json_str)


def merge_dicts(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge two dictionaries."""
    result = base_dict.copy()

    for key, value in update_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def is_valid_uuid(val: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
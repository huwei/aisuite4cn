from __future__ import annotations

import re
import uuid


# ... existing code ...

def to_pascal_case(text: str) -> str:
    """Convert string to Pascal case."""
    # Split by hyphens, underscores, or spaces
    words = re.split(r'[-_\s]+', text)
    # Capitalize first letter of each word and join
    return ''.join(word.capitalize() for word in words if word)


def to_snake_case(text: str) -> str:
    """Convert string to snake case."""
    # Split by hyphens, underscores, or camelCase boundaries
    # First, handle camelCase by inserting underscore before uppercase letters
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
    # Then split by hyphens, underscores, or spaces
    words = re.split(r'[-_\s]+', text)
    # Convert to lowercase and join with underscores
    return '_'.join(word.lower() for word in words if word)


def generate_id(prefix: str = "") -> str:
    """Generate a unique id string, optionally prefixed."""
    return prefix + uuid.uuid4().hex

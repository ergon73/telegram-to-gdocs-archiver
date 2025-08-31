"""Helper utilities."""
from typing import Any, Dict
import json
from datetime import datetime

def safe_json_serialize(obj: Any) -> str:
    """Safely serialize object to JSON."""
    try:
        return json.dumps(obj, default=str)
    except Exception:
        return str(obj)

def format_timestamp(dt: datetime) -> str:
    """Format datetime to string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

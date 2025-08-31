"""Message formatting utilities."""
from typing import List
from src.telegram.models import MessageData

def format_messages_for_gdocs(messages: List[MessageData]) -> str:
    """Format messages for Google Docs insertion."""
    if not messages:
        return ""
    
    formatted_parts = []
    for message in messages:
        formatted_parts.append(message.to_formatted_text())
    
    return "\n\n".join(formatted_parts)

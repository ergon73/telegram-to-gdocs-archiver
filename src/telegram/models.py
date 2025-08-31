"""Telegram data models with enhanced link handling."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import re

class MessageData(BaseModel):
    """Represents a Telegram message with link support."""
    
    id: int = Field(..., description="Message ID")
    text: str = Field(..., description="Message text")
    date: datetime = Field(..., description="Message timestamp")
    channel_id: int = Field(..., description="Channel ID")
    channel_name: Optional[str] = Field(None, description="Channel name")
    channel_username: Optional[str] = Field(None, description="Channel username for links")
    
    # Forward information
    forward_from_channel_id: Optional[int] = None
    forward_from_channel_name: Optional[str] = None
    forward_from_channel_username: Optional[str] = None
    forward_from_user_name: Optional[str] = None
    forward_original_date: Optional[datetime] = None
    forward_message_id: Optional[int] = None  # ID исходного сообщения
    
    # Media information
    has_media: bool = Field(default=False)
    media_type: Optional[str] = None
    media_caption: Optional[str] = None
    
    # Links
    original_link: Optional[str] = None
    forward_original_link: Optional[str] = None  # Ссылка на оригинальное сообщение
    
    def generate_telegram_link(self, channel_username: str, message_id: int) -> Optional[str]:
        """Generate Telegram link from username and message ID."""
        if not channel_username or not message_id:
            return None
            
        # Clean username (remove @ if present)
        username = channel_username.lstrip('@')
        
        # Check if it's a channel ID (starts with -100)
        if username.startswith('-100'):
            # For private channels, we can't generate public links
            return f"telegram://privatelink/{message_id}"
        
        # For public channels
        return f"https://t.me/{username}/{message_id}"
    
    def extract_all_links(self) -> list:
        """Extract all URLs from message text."""
        if not self.text:
            return []
        
        # Pattern for URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, self.text)
    
    def to_formatted_text(self) -> str:
        """Format message for Google Docs (deprecated - use docs_client methods)."""
        from src.config.constants import DATE_FORMAT, MESSAGE_SEPARATOR
        
        parts = []
        
        # Header
        date_str = self.date.strftime(DATE_FORMAT)
        source = self.forward_from_channel_name or self.channel_name or "Unknown"
        parts.append(f"[{date_str}] | Source: {source}")
        
        # Forward info
        if self.forward_from_channel_name:
            parts.append(f"Forwarded from: {self.forward_from_channel_name}")
            if self.forward_original_date:
                parts.append(f"Original date: {self.forward_original_date.strftime(DATE_FORMAT)}")
        
        # Main content
        parts.append("")  # Empty line
        if self.media_caption:
            parts.append(f"[{self.media_type}] {self.media_caption}")
        parts.append(self.text)
        
        # Link - теперь будет кликабельной
        if self.original_link:
            parts.append("")
            parts.append("📎 View in Telegram")  # Этот текст станет ссылкой
        
        # Separator
        parts.append("")
        parts.append(MESSAGE_SEPARATOR)
        parts.append("")
        
        return "\n".join(parts)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

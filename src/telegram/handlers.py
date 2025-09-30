"""Telegram message handlers."""
from typing import Optional
from loguru import logger
from src.telegram.models import TelegramMessage

async def handle_new_message(message) -> Optional[TelegramMessage]:
    """Handle new Telegram message."""
    try:
        logger.debug(f"Handling message {message.id}")
        return TelegramMessage(
            id=getattr(message, "id", 0),
            date=str(getattr(message, "date", "")),
            sender_id=getattr(message, "sender_id", 0),
            text=getattr(message, "text", ""),
        )
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return None

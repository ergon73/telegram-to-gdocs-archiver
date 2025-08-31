"""Telegram message handlers."""
from typing import Optional
from loguru import logger
from src.telegram.models import MessageData

async def handle_new_message(message) -> Optional[MessageData]:
    """Handle new Telegram message."""
    try:
        # This function is kept for compatibility with original structure
        # The actual message processing is now done in TelegramClient.parse_message()
        logger.debug(f"Handling message {message.id}")
        return None
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        return None

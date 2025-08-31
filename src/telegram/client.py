"""Telegram client implementation with enhanced link extraction."""
import asyncio
from typing import Optional, Callable, List
from telethon import TelegramClient as TelethonClient
from telethon.events import NewMessage
from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument, Channel, User
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import Settings
from src.telegram.models import MessageData
from src.exceptions.custom import TelegramConnectionError

class TelegramClient:
    """Handles Telegram operations with link support."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = TelethonClient(
            str(settings.telegram_session_name),
            settings.telegram_api_id,
            settings.telegram_api_hash
        )
        self._channel_cache = {}
        self._handler = None
        
    async def start(self) -> None:
        """Start Telegram client."""
        try:
            await self.client.start()
            logger.info("Telegram client started successfully")
            
            # Test connection
            me = await self.client.get_me()
            logger.info(f"Logged in as: {me.username or me.phone}")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram client: {e}")
            raise TelegramConnectionError(f"Connection failed: {e}")
    
    async def stop(self) -> None:
        """Stop Telegram client."""
        # Remove event handler if exists
        if self._handler:
            self.client.remove_event_handler(self._handler)
            self._handler = None
            
        await self.client.disconnect()
        logger.info("Telegram client stopped")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_channel_info(self, channel_id: int) -> dict:
        """Get detailed channel information with username."""
        if channel_id in self._channel_cache:
            return self._channel_cache[channel_id]
        
        try:
            entity = await self.client.get_entity(channel_id)
            
            # Extract all possible information
            info = {
                'id': entity.id,
                'name': None,
                'username': None,
                'is_private': True
            }
            
            # For channels
            if isinstance(entity, Channel):
                info['name'] = entity.title
                info['username'] = entity.username  # Public channel username
                info['is_private'] = entity.username is None
            # For users (if forwarded from user)
            elif isinstance(entity, User):
                info['name'] = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
                info['username'] = entity.username
            else:
                # Fallback
                info['name'] = getattr(entity, 'title', None) or getattr(entity, 'username', 'Unknown')
                info['username'] = getattr(entity, 'username', None)
            
            self._channel_cache[channel_id] = info
            return info
            
        except Exception as e:
            logger.warning(f"Failed to get channel info for {channel_id}: {e}")
            return {
                'id': channel_id, 
                'name': 'Unknown',
                'username': None,
                'is_private': True
            }
    
    def generate_message_link(self, channel_info: dict, message_id: int) -> Optional[str]:
        """Generate link to a Telegram message."""
        username = channel_info.get('username')
        
        if username:
            # Public channel - generate direct link
            return f"https://t.me/{username}/{message_id}"
        else:
            # Private channel - try to generate private link format
            channel_id = channel_info.get('id')
            if channel_id:
                # Convert channel ID to the format used in private links
                # Private channels have IDs starting with -100
                if str(channel_id).startswith('-100'):
                    # Remove -100 prefix and convert to base64-like format
                    clean_id = str(channel_id)[4:]  # Remove -100
                    return f"https://t.me/c/{clean_id}/{message_id}"
            
            return None
    
    async def parse_message(self, message: Message) -> MessageData:
        """Parse Telethon message to MessageData with enhanced link support."""
        try:
            # Get channel info
            channel_info = await self.get_channel_info(self.settings.telegram_channel_id)
            
            # Basic information
            data = {
                'id': message.id,
                'text': message.text or '',
                'date': message.date,
                'channel_id': self.settings.telegram_channel_id,
                'channel_name': channel_info['name'],
                'channel_username': channel_info['username'],
            }
            
            # Generate original link
            data['original_link'] = self.generate_message_link(channel_info, message.id)
            
            # Forward information
            if message.fwd_from:
                logger.debug(f"Processing forward from: {message.fwd_from}")
                if message.fwd_from.from_id:
                    # Get forward source info
                    try:
                        if hasattr(message.fwd_from.from_id, 'channel_id'):
                            fwd_channel_id = message.fwd_from.from_id.channel_id
                            logger.debug(f"Forward from channel: {fwd_channel_id}")
                            fwd_info = await self.get_channel_info(fwd_channel_id)
                            data['forward_from_channel_id'] = fwd_channel_id
                            data['forward_from_channel_name'] = fwd_info['name']
                            data['forward_from_channel_username'] = fwd_info['username']
                            
                            # Generate forward link - use channel_post if available
                            forward_message_id = getattr(message.fwd_from, 'channel_post', None)
                            if forward_message_id:
                                data['forward_original_link'] = self.generate_message_link(
                                    fwd_info, 
                                    forward_message_id
                                )
                                logger.debug(f"Generated forward link: {data['forward_original_link']}")
                        elif hasattr(message.fwd_from.from_id, 'user_id'):
                            # Forwarded from user
                            fwd_user_id = message.fwd_from.from_id.user_id
                            logger.debug(f"Forward from user: {fwd_user_id}")
                            fwd_info = await self.get_channel_info(fwd_user_id)
                            data['forward_from_channel_name'] = fwd_info['name']
                            data['forward_from_channel_username'] = fwd_info['username']
                    except Exception as e:
                        logger.warning(f"Failed to get forward info: {e}")
                
                data['forward_original_date'] = message.fwd_from.date
                # Use channel_post if available, otherwise skip forward_message_id
                forward_message_id = getattr(message.fwd_from, 'channel_post', None)
                if forward_message_id:
                    data['forward_message_id'] = forward_message_id
                    logger.debug(f"Forward message ID: {forward_message_id}")
            
            # Media information
            if message.media:
                data['has_media'] = True
                if isinstance(message.media, MessageMediaPhoto):
                    data['media_type'] = 'Photo'
                elif isinstance(message.media, MessageMediaDocument):
                    data['media_type'] = 'Document'
                else:
                    data['media_type'] = 'Media'
                
                # Get caption if exists
                if hasattr(message, 'message') and message.message:
                    data['media_caption'] = message.message
            
            return MessageData(**data)
            
        except Exception as e:
            logger.error(f"Failed to parse message {message.id}: {e}")
            logger.debug(f"Message object: {message}")
            logger.debug(f"Message attributes: {dir(message)}")
            if hasattr(message, 'fwd_from') and message.fwd_from:
                logger.debug(f"Forward attributes: {dir(message.fwd_from)}")
            raise
    
    async def get_messages_batch(self, channel_id: int, limit: int = 10, 
                                min_id: Optional[int] = None) -> List[MessageData]:
        """Get batch of messages from channel."""
        try:
            messages = []
            
            # Check if we're using a bot (bots can't get message history)
            me = await self.client.get_me()
            if me.bot:
                logger.warning("Bot detected - cannot get message history. Only listening for new messages.")
                return []
            
            async for message in self.client.iter_messages(channel_id, limit=limit, min_id=min_id):
                msg_data = await self.parse_message(message)
                messages.append(msg_data)
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get messages batch: {e}")
            return []
    
    async def listen_channel(self, channel_id: int, callback: Callable) -> None:
        """Listen for new messages in channel."""
        @self.client.on(NewMessage(chats=[channel_id]))
        async def handler(event):
            try:
                message_data = await self.parse_message(event.message)
                await callback(message_data)
            except Exception as e:
                logger.error(f"Error handling new message: {e}")
        
        self._handler = handler
        logger.info(f"Started listening to channel {channel_id}")
        
        # Keep running until disconnected
        await self.client.run_until_disconnected()

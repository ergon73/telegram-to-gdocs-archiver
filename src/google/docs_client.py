"""Google Docs client implementation with enhanced visual formatting."""
import asyncio
from typing import List, Dict, Any, Tuple, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path
import pickle
import re
from datetime import datetime
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import Settings
from src.telegram.models import MessageData
from src.exceptions.custom import GoogleDocsError

class GoogleDocsWriter:
    """Handles Google Docs operations with visual enhancements."""
    
    SCOPES = ['https://www.googleapis.com/auth/documents']
    
    # Эмодзи для разных типов контента
    MEDIA_EMOJIS = {
        'Photo': '📷',
        'Video': '📹',
        'Audio': '🎵',
        'Document': '📄',
        'Voice': '🎤',
        'Sticker': '🎨',
        'Media': '📎'
    }
    
    # Цветовые схемы (RGB значения от 0.0 до 1.0)
    COLORS = {
        'link': {'red': 0.0, 'green': 0.4, 'blue': 1.0},  # Синий для ссылок
        'header': {'red': 0.2, 'green': 0.2, 'blue': 0.2},  # Темно-серый для заголовков
        'forward': {'red': 0.5, 'green': 0.3, 'blue': 0.7},  # Фиолетовый для форвардов
        'date': {'red': 0.3, 'green': 0.6, 'blue': 0.3},  # Зеленый для дат
        'media': {'red': 0.8, 'green': 0.4, 'blue': 0.0},  # Оранжевый для медиа
        'batch_header': {'red': 0.3, 'green': 0.3, 'blue': 0.8},  # Синий для заголовков батчей
        'batch_footer': {'red': 0.4, 'green': 0.6, 'blue': 0.4},  # Зеленый для футеров батчей
    }
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.service = None
        self.creds = None
        self._initialize_service()
        
    def _initialize_service(self):
        """Initialize Google Docs service."""
        try:
            # Token file path
            token_path = Path('data/state/token.pickle')
            
            # Load existing token
            if token_path.exists():
                with open(token_path, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # Refresh or create new token
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.settings.google_credentials_path), 
                        self.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save token
                token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(token_path, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # Build service
            self.service = build('docs', 'v1', credentials=self.creds)
            logger.info("Google Docs service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Docs service: {e}")
            raise GoogleDocsError(f"Initialization failed: {e}")
    
    def _clean_url(self, url: str) -> str:
        """Clean and validate URL."""
        if not url:
            return url
            
        # Remove trailing punctuation and whitespace
        url = url.rstrip('.,;!? \t\n\r')
        
        # Remove trailing closing parenthesis if it's not part of the URL
        if url.endswith(')'):
            # Check if this is a valid URL with parentheses (like GitHub URLs with parentheses in path)
            # If it's just a trailing ), remove it
            if not any(char in url[:-1] for char in '()'):
                url = url[:-1]
        
        # Fix common URL issues
        if url.startswith('http https://'):
            url = url.replace('http https://', 'https://')
        
        # Remove any remaining problematic characters at the end
        url = url.rstrip('.,;!? \t\n\r)')
        
        # Ensure URL starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            if url.startswith('//'):
                url = 'https:' + url
            else:
                url = 'https://' + url
        
        return url
    
    def _extract_links(self, text: str) -> List[Tuple[str, int, int]]:
        """Extract all URLs from text with their positions.
        
        Returns:
            List of tuples (url, start_pos, end_pos)
        """
        if not text:
            return []
            
        links = []
        
        # Pattern for Markdown links: [text](url)
        # More precise pattern that handles trailing punctuation
        markdown_pattern = r'\[([^\]]+)\]\(([^)]+?)\)'
        for match in re.finditer(markdown_pattern, text):
            url = self._clean_url(match.group(2))
            if url:  # Only add if URL is valid after cleaning
                links.append((url, match.start(), match.end()))
        
        # Pattern for plain URLs (fallback)
        # More precise pattern that doesn't capture trailing punctuation
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        for match in re.finditer(url_pattern, text):
            url = self._clean_url(match.group())
            if url:  # Only add if URL is valid after cleaning
                links.append((url, match.start(), match.end()))
        
        return links
    
    def _create_insert_request(self, text: str, index: int) -> Dict[str, Any]:
        """Create insert text request."""
        return {
            'insertText': {
                'location': {'index': index},
                'text': text
            }
        }
    
    def _validate_color(self, color: Dict) -> Dict:
        """Validate and normalize RGB color values (0.0 to 1.0)."""
        if not color:
            return color
            
        validated = {}
        for component in ['red', 'green', 'blue']:
            if component in color:
                value = color[component]
                # Ensure value is between 0.0 and 1.0
                if isinstance(value, int):
                    value = max(0.0, min(1.0, value / 255.0))
                else:
                    value = max(0.0, min(1.0, float(value)))
                validated[component] = value
        
        return validated
    
    def _create_format_request(self, start_index: int, end_index: int,
                             bold: bool = False, italic: bool = False,
                             font_size: int = None, color: Dict = None) -> Dict[str, Any]:
        """Create text format request."""
        request = {
            'updateTextStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'textStyle': {}
            }
        }
        
        fields = []
        
        if bold:
            request['updateTextStyle']['textStyle']['bold'] = True
            fields.append('bold')
        if italic:
            request['updateTextStyle']['textStyle']['italic'] = True
            fields.append('italic')
        if font_size:
            request['updateTextStyle']['textStyle']['fontSize'] = {
                'magnitude': font_size,
                'unit': 'PT'
            }
            fields.append('fontSize')
        if color:
            validated_color = self._validate_color(color)
            request['updateTextStyle']['textStyle']['foregroundColor'] = {
                'color': {
                    'rgbColor': validated_color
                }
            }
            fields.append('foregroundColor')
        
        # Add fields parameter for optimization
        if fields:
            request['updateTextStyle']['fields'] = ','.join(fields)
        
        return request
    
    def _create_link_request(self, start_index: int, end_index: int, url: str) -> Dict[str, Any]:
        """Create link request."""
        return {
            'updateTextStyle': {
                'range': {
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'textStyle': {
                    'link': {'url': url},
                    'foregroundColor': {
                        'color': {
                            'rgbColor': self.COLORS['link']
                        }
                    }
                },
                'fields': 'link,foregroundColor'
            }
        }
    
    def _create_formatted_message_requests(self, message: MessageData, start_index: int) -> Tuple[str, List[Dict]]:
        """Create formatted message with visual enhancements.
        
        Returns:
            Tuple of (formatted_text, list_of_requests)
        """
        from src.config.constants import DATE_FORMAT, MESSAGE_SEPARATOR
        
        requests = []
        parts = []
        
        # === HEADER SECTION ===
        date_str = message.date.strftime(DATE_FORMAT)
        source = message.forward_from_channel_name or message.channel_name or "Unknown"
        source_emoji = "📢" if not message.forward_from_channel_name else "🔄"
        header_line = f"{date_str} | {source_emoji} {source}"
        parts.append(header_line)
        
        # === FORWARD INFO SECTION ===
        if message.forward_from_channel_name:
            forward_text = f"↪️ Forwarded from: {message.forward_from_channel_name}"
            parts.append(forward_text)
            
            if message.forward_original_date:
                orig_date = f"📆 Original: {message.forward_original_date.strftime(DATE_FORMAT)}"
                parts.append(orig_date)
        
        # Empty line before content
        parts.append("")
        
        # === MEDIA SECTION ===
        if message.has_media:
            media_emoji = self.MEDIA_EMOJIS.get(message.media_type, '📎')
            media_text = f"{media_emoji} {message.media_type}"
            
            if message.media_caption:
                media_text += f": {message.media_caption}"
            
            parts.append(media_text)
        
        # === MAIN TEXT SECTION ===
        if message.text:
            parts.append(message.text)
        
        # === TELEGRAM LINK SECTION ===
        if message.original_link:
            parts.append("")  # Empty line
            link_text = "🔗 View in Telegram"
            parts.append(link_text)
            
            # If there's a forward link too
            if hasattr(message, 'forward_original_link') and message.forward_original_link:
                forward_link_text = "🔗 View Original"
                parts.append(forward_link_text)
        
        # === SEPARATOR ===
        parts.append("")
        parts.append(MESSAGE_SEPARATOR)
        parts.append("")
        
        # Create the complete text
        formatted_text = "\n".join(parts)
        
        # Now calculate positions for formatting
        current_pos = start_index
        
        # Format header
        header_end = current_pos + len(header_line)
        requests.append(self._create_format_request(
            current_pos,
            header_end,
            bold=True,
            font_size=12,
            color=self.COLORS['header']
        ))
        current_pos = header_end + 1  # +1 for newline
        
        # Format forward info
        if message.forward_from_channel_name:
            forward_end = current_pos + len(forward_text)
            requests.append(self._create_format_request(
                current_pos,
                forward_end,
                italic=True,
                color=self.COLORS['forward']
            ))
            current_pos = forward_end + 1
            
            if message.forward_original_date:
                orig_date_end = current_pos + len(orig_date)
                requests.append(self._create_format_request(
                    current_pos,
                    orig_date_end,
                    italic=True,
                    font_size=10,
                    color=self.COLORS['date']
                ))
                current_pos = orig_date_end + 1
        
        # Skip empty line
        current_pos += 1
        
        # Format media info
        if message.has_media:
            media_end = current_pos + len(media_text)
            requests.append(self._create_format_request(
                current_pos,
                media_end,
                bold=True,
                color=self.COLORS['media']
            ))
            current_pos = media_end + 1
        
        # Format links in main text
        if message.text:
            text_start = current_pos
            # Find and format URLs in text
            links = self._extract_links(message.text)
            logger.debug(f"Found {len(links)} links in message text: {links}")
            for url, rel_start, rel_end in links:
                abs_start = text_start + rel_start
                abs_end = text_start + rel_end
                logger.debug(f"Creating link request for URL: {url} at positions {abs_start}-{abs_end}")
                requests.append(self._create_link_request(abs_start, abs_end, url))
            current_pos += len(message.text) + 1
        
        # Format Telegram links
        if message.original_link:
            current_pos += 1  # Skip empty line
            link_end = current_pos + len(link_text)
            requests.append(self._create_link_request(
                current_pos,
                link_end,
                message.original_link
            ))
            current_pos = link_end + 1
            
            if hasattr(message, 'forward_original_link') and message.forward_original_link:
                forward_link_end = current_pos + len(forward_link_text)
                requests.append(self._create_link_request(
                    current_pos,
                    forward_link_end,
                    message.forward_original_link
                ))
        
        return formatted_text, requests
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def write_message(self, message: MessageData) -> bool:
        """Write a single message to Google Docs with enhanced formatting."""
        try:
            # Get document
            doc = self.service.documents().get(documentId=self.settings.google_doc_id).execute()
            current_length = doc['body']['content'][-1]['endIndex']
            
            # Create formatted message
            formatted_text, format_requests = self._create_formatted_message_requests(message, current_length - 1)
            
            # Prepare all requests
            all_requests = [
                self._create_insert_request(formatted_text, current_length - 1)
            ]
            all_requests.extend(format_requests)
            
            # Execute batch update
            if all_requests:
                try:
                    result = self.service.documents().batchUpdate(
                        documentId=self.settings.google_doc_id,
                        body={'requests': all_requests}
                    ).execute()
                    logger.info(f"Written message {message.id} with enhanced formatting")
                except HttpError as e:
                    logger.error(f"Google Docs API error: {e}")
                    # Fallback to simple text insertion without formatting
                    fallback_request = self._create_insert_request(formatted_text, current_length - 1)
                    self.service.documents().batchUpdate(
                        documentId=self.settings.google_doc_id,
                        body={'requests': [fallback_request]}
                    ).execute()
                    logger.info(f"Written message {message.id} without formatting (fallback)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write message: {e}")
            raise GoogleDocsError(f"Write failed: {e}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def write_batch(self, messages: List[MessageData]) -> bool:
        """Write batch of messages with enhanced batch formatting."""
        try:
            # Get document
            doc = self.service.documents().get(documentId=self.settings.google_doc_id).execute()
            current_length = doc['body']['content'][-1]['endIndex']
            
            # Prepare batch header
            now = datetime.now()
            header = f"\n📦 BATCH UPDATE - {now.strftime('%Y-%m-%d %H:%M:%S')} - {len(messages)} messages\n"
            header += "─" * 60 + "\n"
            
            all_requests = [
                self._create_insert_request(header, current_length - 1)
            ]
            
            # Format batch header
            header_start = current_length - 1
            header_end = header_start + len(header)
            all_requests.append(self._create_format_request(
                header_start,
                header_end,
                bold=True,
                font_size=12,
                color=self.COLORS['batch_header']
            ))
            
            current_position = header_end
            
            # === PROCESS EACH MESSAGE ===
            for i, message in enumerate(messages):
                # Create formatted text and requests for this message
                formatted_text, format_requests = self._create_formatted_message_requests(
                    message, current_position
                )
                
                # Add insert request
                all_requests.append(self._create_insert_request(formatted_text, current_position))
                
                # Add formatting requests
                all_requests.extend(format_requests)
                
                # Update position for next message
                current_position += len(formatted_text)
            
            # === BATCH FOOTER ===
            footer = f"\n{'─' * 60}\n✅ Batch completed at {now.strftime('%H:%M:%S')}\n\n"
            all_requests.append(self._create_insert_request(footer, current_position))
            
            # Format footer
            all_requests.append(self._create_format_request(
                current_position,
                current_position + len(footer),
                italic=True,
                font_size=10,
                color=self.COLORS['batch_footer']
            ))
            
            # Execute batch update
            if all_requests:
                try:
                    result = self.service.documents().batchUpdate(
                        documentId=self.settings.google_doc_id,
                        body={'requests': all_requests}
                    ).execute()
                    logger.info(f"Written batch of {len(messages)} messages with enhanced formatting")
                except HttpError as e:
                    logger.error(f"Google Docs API error: {e}")
                    # Fallback to simple text insertion without formatting
                    fallback_requests = [self._create_insert_request(footer, current_position)]
                    self.service.documents().batchUpdate(
                        documentId=self.settings.google_doc_id,
                        body={'requests': fallback_requests}
                    ).execute()
                    logger.info(f"Written batch of {len(messages)} messages without formatting (fallback)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write batch: {e}")
            raise GoogleDocsError(f"Batch write failed: {e}")
    
    def test_connection(self) -> bool:
        """Test Google Docs connection with a simple test message."""
        try:
            doc = self.service.documents().get(documentId=self.settings.google_doc_id).execute()
            logger.info(f"Connected to document: {doc.get('title', 'Untitled')}")
            
            # Add a simple test message without formatting first
            current_length = doc['body']['content'][-1]['endIndex']
            insert_index = current_length - 1
            
            test_message = f"\n=== ARCHIVER TEST {datetime.now().strftime('%H:%M:%S')} ===\n"
            
            # Simple insert without formatting
            request = self._create_insert_request(test_message, insert_index)
            
            # Execute test
            self.service.documents().batchUpdate(
                documentId=self.settings.google_doc_id,
                body={'requests': [request]}
            ).execute()
            
            logger.success("✅ Test connection successful - simple test message added")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Google Doc: {e}")
            return False

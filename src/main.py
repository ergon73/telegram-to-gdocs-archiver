"""Main application entry point."""
import asyncio
import signal
import sys
from typing import Optional
from pathlib import Path
from loguru import logger
import click

from src.config.settings import Settings
from src.telegram.client import TelegramClient
from src.telegram.models import MessageData  
from src.google.docs_client import GoogleDocsWriter
from src.storage.state import StateManager
from src.utils.logger import setup_logging
from src.utils.decorators import measure_time
from src.exceptions.custom import ArchiverError

class TelegramToGDocsArchiver:
    """Main application class."""
    
    def __init__(self):
        """Initialize the archiver."""
        try:
            # Load settings
            self.settings = Settings()
            
            # Setup logging
            setup_logging(self.settings.log_file_path, self.settings.debug_mode)
            logger.info("Initializing Telegram to Google Docs Archiver")
            
            # Initialize components
            self.state = StateManager(self.settings.state_db_path)
            self.telegram = TelegramClient(self.settings)
            self.gdocs = GoogleDocsWriter(self.settings)
            
            # Message buffer
            self.message_buffer = []
            self.running = False
            self._shutdown_event = asyncio.Event()
            
            # Setup signal handlers
            signal.signal(signal.SIGINT, self._handle_shutdown)
            signal.signal(signal.SIGTERM, self._handle_shutdown)
            
        except Exception as e:
            logger.error(f"Failed to initialize archiver: {e}")
            raise ArchiverError(f"Initialization failed: {e}")
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signal."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self._shutdown_event.set()
    
    async def process_message(self, message: MessageData) -> None:
        """Process a single message."""
        try:
            logger.debug(f"Processing message {message.id}")
            
            # Add to buffer
            self.message_buffer.append(message)
            
            # Check if we should flush
            if len(self.message_buffer) >= self.settings.batch_size:
                await self.flush_buffer()
                
        except Exception as e:
            logger.error(f"Failed to process message {message.id}: {e}")
    
    @measure_time
    async def flush_buffer(self) -> None:
        """Flush message buffer to Google Docs."""
        if not self.message_buffer:
            return
        
        try:
            logger.info(f"Flushing buffer with {len(self.message_buffer)} messages")
            
            # Write to Google Docs
            success = await self.gdocs.write_batch(self.message_buffer)
            
            if success:
                # Update state
                last_message = self.message_buffer[-1]
                self.state.set_last_message_id(
                    self.settings.telegram_channel_id,
                    last_message.id
                )
                
                # Update stats
                self.state.update_stats(processed=len(self.message_buffer))
                
                # Clear buffer
                self.message_buffer.clear()
                self.state.clear_pending_batch()
                
                logger.info("Buffer flushed successfully")
            else:
                # Save to pending for retry
                self.state.save_pending_batch(self.message_buffer)
                logger.warning("Failed to flush buffer, saved to pending")
                
        except Exception as e:
            logger.error(f"Error flushing buffer: {e}")
            self.state.save_pending_batch(self.message_buffer)
            self.state.update_stats(error=True)
    
    async def process_pending(self) -> None:
        """Process pending messages from previous run."""
        pending = self.state.get_pending_batch()
        if pending:
            logger.info(f"Found {len(pending)} pending messages from previous run")
            
            # Convert back to MessageData objects
            self.message_buffer = [MessageData(**msg) for msg in pending]
            
            # Try to flush
            await self.flush_buffer()
    
    async def catch_up(self) -> None:
        """Catch up on missed messages."""
        try:
            last_id = self.state.get_last_message_id(self.settings.telegram_channel_id)
            
            if last_id:
                logger.info(f"Catching up from message ID {last_id}")
                
                # Get missed messages
                messages = await self.telegram.get_messages_batch(
                    self.settings.telegram_channel_id,
                    limit=100,
                    min_id=last_id
                )
                
                if messages:
                    logger.info(f"Found {len(messages)} missed messages")
                    for msg in reversed(messages):  # Process in chronological order
                        await self.process_message(msg)
                    
                    # Flush any remaining
                    await self.flush_buffer()
            else:
                logger.info("No previous message ID found, starting fresh")
                
        except Exception as e:
            logger.error(f"Failed to catch up: {e}")
    
    async def periodic_flush(self) -> None:
        """Periodically flush buffer."""
        while self.running:
            try:
                # Wait for check interval or shutdown signal
                await asyncio.wait_for(
                    asyncio.create_task(self._shutdown_event.wait()), 
                    timeout=self.settings.check_interval
                )
                break  # Shutdown signal received
            except asyncio.TimeoutError:
                # Normal timeout, continue with flush
                if self.message_buffer:
                    logger.debug(f"Periodic flush triggered, {len(self.message_buffer)} messages in buffer")
                    await self.flush_buffer()
    
    async def run(self) -> None:
        """Main application loop."""
        try:
            self.running = True
            logger.info("Starting archiver...")
            
            # Test Google Docs connection
            if not self.gdocs.test_connection():
                raise ArchiverError("Failed to connect to Google Docs")
            
            # Start Telegram client
            await self.telegram.start()
            
            # Process any pending messages
            await self.process_pending()
            
            # Catch up on missed messages
            await self.catch_up()
            
            # Start periodic flush task
            flush_task = asyncio.create_task(self.periodic_flush())
            
            # Listen for new messages with timeout
            logger.info(f"Listening to channel {self.settings.telegram_channel_id}")
            
            # Create a task for listening to messages
            listen_task = asyncio.create_task(
                self.telegram.listen_channel(
                    self.settings.telegram_channel_id,
                    self.process_message
                )
            )
            
            # Wait for either shutdown signal or listen task completion
            done, pending = await asyncio.wait(
                [listen_task, asyncio.create_task(self._shutdown_event.wait())],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel listen task if shutdown was requested
            if not self.running:
                listen_task.cancel()
                try:
                    await listen_task
                except asyncio.CancelledError:
                    pass
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        logger.info("Cleaning up...")
        
        # Final flush
        if self.message_buffer:
            logger.info(f"Final flush of {len(self.message_buffer)} messages")
            await self.flush_buffer()
        
        # Stop components
        await self.telegram.stop()
        self.state.close()
        
        logger.info("Cleanup completed")

@click.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--test', is_flag=True, help='Test connections and exit')
def main(debug: bool, test: bool):
    """Telegram to Google Docs Archiver."""
    try:
        # Create archiver
        archiver = TelegramToGDocsArchiver()
        
        if test:
            # Test mode
            logger.info("Running in test mode")
            
            # Test Google Docs
            if archiver.gdocs.test_connection():
                logger.success("✓ Google Docs connection successful")
            else:
                logger.error("✗ Google Docs connection failed")
            
            # Show stats
            stats = archiver.state.get_stats()
            logger.info(f"Stats: {stats}")
            
            return
        
        # Run archiver
        asyncio.run(archiver.run())
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

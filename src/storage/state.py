"""State management for persistence."""
from typing import Optional, List, Any, Dict
from pathlib import Path
from sqlitedict import SqliteDict
from datetime import datetime
from loguru import logger
import json

from src.telegram.models import MessageData

class StateManager:
    """Manages application state with persistence."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = None
        self._open_db()
        logger.info(f"State manager initialized with db: {db_path}")
    
    def _open_db(self):
        """Open database connection."""
        try:
            self.db = SqliteDict(str(self.db_path), autocommit=True)
        except Exception as e:
            logger.error(f"Failed to open database: {e}")
            # Try to remove corrupted database
            try:
                self.db_path.unlink(missing_ok=True)
                self.db_path.with_suffix('.db-journal').unlink(missing_ok=True)
                self.db = SqliteDict(str(self.db_path), autocommit=True)
            except Exception as e2:
                logger.error(f"Failed to recreate database: {e2}")
                raise
    
    def get_last_message_id(self, channel_id: int) -> Optional[int]:
        """Get last processed message ID for channel."""
        key = f"last_msg_{channel_id}"
        return self.db.get(key)
    
    def set_last_message_id(self, channel_id: int, message_id: int) -> None:
        """Set last processed message ID for channel."""
        key = f"last_msg_{channel_id}"
        self.db[key] = message_id
        logger.debug(f"Updated last message ID for channel {channel_id}: {message_id}")
    
    def get_pending_batch(self) -> List[Dict[str, Any]]:
        """Get pending messages batch."""
        data = self.db.get("pending_batch", [])
        return data
    
    def save_pending_batch(self, messages: List[MessageData]) -> None:
        """Save pending messages batch."""
        data = [msg.dict() for msg in messages]
        self.db["pending_batch"] = data
        logger.info(f"Saved {len(messages)} messages to pending batch")
    
    def clear_pending_batch(self) -> None:
        """Clear pending batch."""
        if "pending_batch" in self.db:
            del self.db["pending_batch"]
            logger.debug("Cleared pending batch")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.db.get("stats", {
            "total_processed": 0,
            "last_run": None,
            "errors_count": 0
        })
        return stats
    
    def update_stats(self, processed: int = 0, error: bool = False) -> None:
        """Update processing statistics."""
        stats = self.get_stats()
        stats["total_processed"] += processed
        stats["last_run"] = datetime.now().isoformat()
        if error:
            stats["errors_count"] += 1
        self.db["stats"] = stats
    
    def close(self) -> None:
        """Close database connection."""
        if self.db:
            try:
                self.db.close()
                logger.debug("State manager closed")
            except Exception as e:
                logger.warning(f"Error closing database: {e}")
    
    def __del__(self):
        """Destructor to ensure database is closed."""
        self.close()

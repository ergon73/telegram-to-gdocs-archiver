"""Cache management utilities."""
from typing import Any, Optional
from datetime import datetime, timedelta
import json
from loguru import logger

class CacheManager:
    """Simple in-memory cache manager."""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            item = self.cache[key]
            if datetime.now() < item['expires']:
                return item['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self.cache[key] = {
            'value': value,
            'expires': datetime.now() + timedelta(seconds=self.ttl)
        }
    
    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
        logger.debug("Cache cleared")

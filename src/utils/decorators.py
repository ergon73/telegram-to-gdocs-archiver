"""Utility decorators."""
import asyncio
from functools import wraps
from typing import Callable, Any
from loguru import logger
import time

def measure_time(func: Callable) -> Callable:
    """Measure function execution time."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start
            logger.debug(f"{func.__name__} took {elapsed:.2f}s")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start
            logger.debug(f"{func.__name__} took {elapsed:.2f}s")
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

def safe_async(func: Callable) -> Callable:
    """Safely execute async function with error handling."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return None
    return wrapper

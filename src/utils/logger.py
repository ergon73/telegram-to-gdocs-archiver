"""Logging configuration."""
from loguru import logger
from pathlib import Path
import sys

def setup_logging(log_file_path: Path, debug: bool = False):
    """Configure application logging."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler
    level = "DEBUG" if debug else "INFO"
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # File handler
    logger.add(
        str(log_file_path),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    logger.info(f"Logging configured. File: {log_file_path}, Debug: {debug}")

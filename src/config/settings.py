"""Configuration management with validation."""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator, Field
import os

class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Telegram settings
    telegram_api_id: int = Field(..., description="Telegram API ID")
    telegram_api_hash: str = Field(..., description="Telegram API Hash")
    telegram_channel_id: int = Field(..., description="Target Telegram channel ID")
    telegram_session_name: str = Field(default="archiver_bot", description="Session name")
    
    # Google settings
    google_doc_id: str = Field(..., description="Google Document ID")
    google_credentials_path: Path = Field(default="credentials.json", description="Path to Google credentials")
    
    # Processing settings
    batch_size: int = Field(default=5, ge=1, le=50, description="Messages per batch")
    check_interval: int = Field(default=30, ge=10, description="Check interval in seconds")
    max_retries: int = Field(default=3, ge=1, description="Max retry attempts")
    
    # Features
    enable_cache: bool = Field(default=True, description="Enable caching")
    debug_mode: bool = Field(default=False, description="Debug mode")
    
    # Paths
    state_db_path: Path = Field(default="data/state/state.db", description="State database path")
    log_file_path: Path = Field(default="data/logs/archiver.log", description="Log file path")
    
    @validator('google_credentials_path')
    def validate_credentials_path(cls, v):
        if not v.exists():
            raise ValueError(f"Google credentials file not found: {v}")
        return v
    
    @validator('state_db_path', 'log_file_path', pre=True)
    def create_parent_dirs(cls, v):
        path = Path(v)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    
    class Config:
        env_file = ".env"
        case_sensitive = False

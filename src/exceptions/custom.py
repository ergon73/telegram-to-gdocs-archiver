"""Custom exceptions."""

class ArchiverError(Exception):
    """Base exception for archiver."""
    pass

class TelegramConnectionError(ArchiverError):
    """Telegram connection error."""
    pass

class GoogleDocsError(ArchiverError):
    """Google Docs operation error."""
    pass

class ConfigurationError(ArchiverError):
    """Configuration error."""
    pass

class StateError(ArchiverError):
    """State management error."""
    pass

"""Application constants."""

# Message formatting
MESSAGE_SEPARATOR = "═" * 50
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Google Docs formatting
GDOCS_TITLE_STYLE = {
    'bold': True,
    'fontSize': {'magnitude': 14, 'unit': 'PT'}
}

GDOCS_BODY_STYLE = {
    'fontSize': {'magnitude': 11, 'unit': 'PT'}
}

# Rate limits
GOOGLE_API_QUOTA_PER_MINUTE = 60
TELEGRAM_API_CALLS_PER_SECOND = 5

# Retry settings
RETRY_EXPONENTIAL_BASE = 2
RETRY_MAX_WAIT = 60

# Cache settings
CACHE_TTL_SECONDS = 3600

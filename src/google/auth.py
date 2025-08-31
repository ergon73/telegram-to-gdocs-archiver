"""Google authentication utilities."""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path
import pickle
from loguru import logger

def get_gdocs_service(credentials_path: str):
    """Get Google Docs service instance."""
    try:
        # Token file path
        token_path = Path('data/state/token.pickle')
        
        # Load existing token
        creds = None
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or create new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, 
                    ['https://www.googleapis.com/auth/documents']
                )
                creds = flow.run_local_server(port=0)
            
            # Save token
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build service
        service = build('docs', 'v1', credentials=creds)
        logger.info("Google Docs service created successfully")
        return service
        
    except Exception as e:
        logger.error(f"Failed to create Google Docs service: {e}")
        raise

# Configure logging
import datetime as dt
import logging
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

def create_logging(name, log_file, level=logging.INFO):
    """Configure a logger with file and console output"""

    # Create logs directory if needed
    os.makedirs('logs', exist_ok=True)

    # Unique logger instance
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    # File handler
    file_handler = logging.FileHandler(
        f"logs/{log_file}"
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s - %(message)s'
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def authenticate(token_file, credentials_file, scopes, logger) -> Credentials:
    """
    Handles OAuth2 authentication flow for Google Drive API access.
    Steps:
    1. Checks for existing valid credentials in token.json
    2. Refreshes token if expired
    3. Initiates new auth flow if no valid credentials exist
    4. Stores new credentials for future use
    Returns: Credentials: Authenticated credentials object
    Raises: Exception: If authentication fails
    """
    try:
        creds = None

        # Load existing credentials if available
        if os.path.exists(token_file):
            logger.debug("Loading existing credentials")
            creds = Credentials.from_authorized_user_file(token_file, scopes)

        # Refresh or create new credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                logger.info("Initiating new authentication flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, scopes)
                creds = flow.run_local_server(port=0)

            # Store the credentials for the next run
            logger.debug("Storing new credentials")
            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        return creds

    except Exception as e:
        logger.error("Authentication failed", exc_info=True)
        raise

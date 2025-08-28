# Configure logging
import datetime as dt
import logging
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import config


def create_logging(name, log_file, level=logging.INFO):
    """Configure a logger with file and console output"""

    os.makedirs(config.LOGS_FOLDER, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    file_handler = logging.FileHandler(f"{config.LOGS_FOLDER}/{log_file}")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def authenticate(token_file, credentials_file, scopes, logger) -> Credentials:
    """
    Handles OAuth2 authentication flow for Google Drive API access.
    """
    try:
        creds = None

        if os.path.exists(token_file):
            logger.debug(f"Loading existing credentials from {token_file}")
            creds = Credentials.from_authorized_user_file(token_file, scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                logger.info("Initiating new authentication flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, scopes
                )
                creds = flow.run_local_server(port=0)

            os.makedirs(os.path.dirname(token_file), exist_ok=True)
            with open(token_file, "w") as token:
                token.write(creds.to_json())

        return creds

    except Exception as e:
        logger.error("Authentication failed", exc_info=True)
        raise

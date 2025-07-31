import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from utils import  create_logging

# Configuration
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_FILE = 'auth/gdrive/token.json'
CREDENTIALS_FILE = 'auth/credentials.json'
DRIVE_FOLDER_ID = '1DBOTcdJQ6WhYIoeZ2L_zqUY98FgVTHrs'  # Your target folder

logger = create_logging('logs/drive_upload.log')

def authenticate() -> Credentials:
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
        if os.path.exists(TOKEN_FILE):
            logger.debug("Loading existing credentials")
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        # Refresh or create new credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                creds.refresh(Request())
            else:
                logger.info("Initiating new authentication flow")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            # Store the credentials for the next run
            logger.debug("Storing new credentials")
            os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

        return creds

    except Exception as e:
        logger.error("Authentication failed", exc_info=True)
        raise


def upload_invoices(month_year: str, drive_folder_id: str) -> bool:
    """
    Uploads all files from a local folder to specified Google Drive folder.
    Process:
    1. Authenticates with Google Drive API
    2. Verifies local folder exists
    3. Uploads each file to target Drive folder
    4. Provides success/failure feedback
    Returns: bool: True if upload succeeded, False otherwise
    """
    try:
        logger.info(f"Starting upload for {month_year} to folder {drive_folder_id[:4]}...")  # Truncate ID for logs

        # Initialize API service
        service = build('drive', 'v3', credentials=authenticate())
        local_folder = os.path.join('Invoices', month_year)

        # Verify source folder
        if not os.path.exists(local_folder):
            logger.error(f"Local folder not found: {local_folder}")
            return False

        # Process each file
        success_count = 0
        for filename in os.listdir(local_folder):
            filepath = os.path.join(local_folder, filename)
            if os.path.isfile(filepath):
                try:
                    logger.debug(f"Processing file: {filename}")

                    file_metadata = {
                        'name': filename,
                        'parents': [drive_folder_id]
                    }
                    media = MediaFileUpload(filepath)

                    service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()

                    success_count += 1
                    logger.info(f"Uploaded: {filename}")
                except Exception as file_error:
                    logger.error(f"Failed to upload {filename}", exc_info=True)

        # Report results
        if success_count > 0:
            logger.info(f"Upload completed with {success_count} successful files")
            return True
        else:
            logger.error("No files were successfully uploaded")
            return False

    except HttpError as error:
        logger.error("Google Drive API error occurred", exc_info=True)
        return False
    except Exception as error:
        logger.error("Unexpected error during upload", exc_info=True)
        return False
import os
from utils import create_logging, authenticate
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Configuration
scopes = ['https://www.googleapis.com/auth/drive']
token_file = 'auth/gdrive/token.json'
credentials_file = 'auth/credentials.json'
# Personal folder
#drive_folder_id = '1DBOTcdJQ6WhYIoeZ2L_zqUY98FgVTHrs'  # Your target folder
# External folder
drive_folder_id = '18zg-iJMVFJWHcoBBb2m3PD_-cO8d_62o'
logger = create_logging('upload', 'upload.log')


def create_drive_folder(service, month_year):
    """
    Creates a new folder in Google Drive for the given month_year
    Returns the new folder ID
    """
    folder_metadata = {
        'name': month_year,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [drive_folder_id]  # Your root folder ID
    }

    try:
        folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        logger.info(f"Created new Drive folder: {month_year} (ID: {folder['id']})")
        return folder['id']

    except HttpError as error:
        logger.error(f"Failed to create folder: {error}")
        raise


def upload_invoices(month_year: str) -> bool:
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
        service = build('drive', 'v3', credentials=authenticate(token_file, credentials_file, scopes, logger))
        target_folder_id = create_drive_folder(service, month_year)
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
                        'parents': [target_folder_id]
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
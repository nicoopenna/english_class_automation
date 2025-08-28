import os
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from utils import authenticate, create_logging
import config

# Initialize logging for this module
logger = create_logging("upload", "upload.log")


def get_or_create_folder_id(drive_service, folder_name: str) -> str:
    """
    Checks if a folder exists in Google Drive and returns its ID.
    If it doesn't exist, it creates it and returns the new ID.

    Parameters:
    - drive_service: The authenticated Google Drive service object.
    - folder_name (str): The name of the folder to check or create.

    Returns:
    - str: The ID of the existing or newly created folder.
    """
    logger.info(f"Checking for existing folder '{folder_name}'...")
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = drive_service.files().list(q=query, spaces="drive").execute()

    if response["files"]:
        folder_id = response["files"][0]["id"]
        logger.info(f"Folder found. ID: {folder_id}")
        return folder_id
    else:
        logger.info(f"Folder not found. Creating a new one...")
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        folder = drive_service.files().create(body=file_metadata, fields="id").execute()
        folder_id = folder.get("id")
        logger.info(f"New folder created. ID: {folder_id}")
        return folder_id


def upload_invoices(prefix: str):
    """
    Uploads all image files from a specific local folder to Google Drive.

    Parameters:
    - prefix (str): The month-year prefix for the local folder (e.g., '09-2025').
    """
    try:
        # Authenticate with Google Drive API using credentials from config
        service = build(
            "drive",
            "v3",
            credentials=authenticate(
                token_file=config.DRIVE_TOKEN_FILE,
                credentials_file=config.CREDENTIALS_FILE,
                scopes=config.DRIVE_SCOPES,
                logger=logger,
            ),
        )
        logger.info("Successfully authenticated with Google Drive")

        # Define the local folder to upload
        invoice_folder_path = os.path.join(config.INVOICES_FOLDER, prefix)

        # Get or create the parent folder on Google Drive
        parent_folder_id = get_or_create_folder_id(service, config.INVOICES_FOLDER)

        # Get or create the specific month subfolder on Google Drive
        subfolder_id = get_or_create_folder_id(service, prefix)

        # Link the subfolder to the parent folder
        service.files().update(
            fileId=subfolder_id, addParents=parent_folder_id
        ).execute()

        # Iterate through local files and upload them
        for root, dirs, files in os.walk(invoice_folder_path):
            for filename in files:
                if filename.endswith(".png"):
                    file_path = os.path.join(root, filename)
                    file_metadata = {"name": filename, "parents": [subfolder_id]}
                    media = MediaFileUpload(file_path, mimetype="image/png")

                    logger.info(f"Uploading file: {filename}")
                    service.files().create(
                        body=file_metadata, media_body=media, fields="id"
                    ).execute()
                    logger.info(f"Successfully uploaded {filename}")

    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}", exc_info=True)

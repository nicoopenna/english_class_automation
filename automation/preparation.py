import os
import csv
from googleapiclient.discovery import build
from .utils import create_logging, authenticate
from . import config
from typing import List

# Initialize logging
logger = create_logging("preparation", "preparation.log")


def download_sheet_data() -> List[list]:
    """
    Downloads columns A-D from Google Sheet.

    Returns:
        List[list]: The raw data from the Google Sheet, or an empty list if
                    download failed.
    """
    try:
        logger.info("Starting Google Sheets data download")

        creds = authenticate(
            token_file=config.SHEETS_TOKEN_FILE,
            credentials_file=config.CREDENTIALS_FILE,
            scopes=config.SHEETS_SCOPES,
            logger=logger,
        )

        service = build("sheets", "v4", credentials=creds)
        logger.debug("Sheets API service initialized")

        logger.info(f"Downloading range {config.SHEET_RANGE} from spreadsheet")
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=config.SPREADSHEET_ID, range=config.SHEET_RANGE)
            .execute()
        )

        values = result.get("values", [])
        if not values:
            logger.warning("No data found in specified range")

        return values

    except Exception as e:
        logger.error(f"Download failed: {str(e)}", exc_info=True)
        return []

import os
import csv
from googleapiclient.discovery import build
from utils import create_logging, authenticate

# Initialize logging
logger = create_logging('preparation', 'preparation.log')
# Configuration
scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
spreadsheet_id = '1vAMoSKzAEh3r0WQxlwYnU1nu1l0VsPQKsCw_Co2GROE'
sheet_range = 'schedule!A:D'
output_csv = 'students.csv'
token_file = 'auth/sheets/token.json'
credentials_file = 'auth/credentials.json'

def download_sheet_data() -> bool:
    """
    Downloads columns A-D from Google Sheet and saves as schedule.csv
    Returns: bool: True if download succeeded, False otherwise
    """


    try:
        logger.info("Starting Google Sheets data download")

        # Authenticate using utils function
        creds = authenticate(
            token_file=token_file,
            credentials_file=credentials_file,
            scopes=scopes,
            logger=logger
        )

        # Initialize Sheets API
        service = build('sheets', 'v4', credentials=creds)
        logger.debug("Sheets API service initialized")

        # Get data from sheet
        logger.info(f"Downloading range {sheet_range} from spreadsheet")
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_range
        ).execute()
        values = result.get('values', [])

        if not values:
            logger.warning("No data found in specified range")
            return False

        # Write to CSV
        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(values)

        logger.info(f"Successfully saved data to {os.path.abspath(output_csv)}")
        return True

    except Exception as e:
        logger.error(f"Download failed: {str(e)}", exc_info=True)
        return False
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import csv


def download_sheet_data():
    """Download columns A-D from Google Sheet and save as schedule.csv"""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SPREADSHEET_ID = '1vAMoSKzAEh3r0WQxlwYnU1nu1l0VsPQKsCw_Co2GROE'
    SHEET_RANGE = 'schedule!A:D'
    OUTPUT_CSV = 'students.csv'

    creds = None
    if os.path.exists('auth/token.json'):
        creds = Credentials.from_authorized_user_file('auth/token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'auth/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('auth/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE
        ).execute()
        values = result.get('values', [])

        if not values:
            print('⚠️ No data found in the specified range.')
            return False

        with open(OUTPUT_CSV, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(values)

        print(f'✅ Downloaded latest data to {os.path.abspath(OUTPUT_CSV)}')
        return True

    except Exception as e:
        print(f'❌ Download failed: {str(e)}')
        return False

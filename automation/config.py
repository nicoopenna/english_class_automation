import os
import datetime

# --- General Configuration ---
PROJECT_NAME = "english_class_automation"

# --- Folder Paths ---
INVOICES_FOLDER = "Invoices"
SUMMARIES_FOLDER = "Summaries"
LOGS_FOLDER = "logs"
AUTH_FOLDER = "auth"

# --- File Paths ---
STUDENTS_CSV_FILE = "data/students.csv"
NON_CLASS_DATES_FILE = "data/non_class_dates.txt"
CREDENTIALS_FILE = os.path.join(AUTH_FOLDER, "credentials.json")
# Separated token files for each service
SHEETS_TOKEN_FILE = os.path.join(AUTH_FOLDER, "gsheets/token.json")
DRIVE_TOKEN_FILE = os.path.join(AUTH_FOLDER, "gdrive/token.json")

# --- Asset Paths ---
LOGO_PATH = "logo.png"
FONT_REGULAR = "Roboto/static/Roboto-Regular.ttf"
FONT_BOLD = "Roboto/static/Roboto-Bold.ttf"

# --- Google Sheets API Configuration ---
SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1vAMoSKzAEh3r0WQxlwYnU1nu1l0VsPQKsCw_Co2GROE'
SHEET_RANGE = 'schedule!A:D'

# --- Google Drive API Configuration ---
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']

# --- Holidays API Configuration ---
HOLIDAYS_API_URL = "https://api.argentinadatos.com/v1/feriados/"
import os
import datetime

# --- General Configuration ---
PROJECT_NAME = "english_class_automation"
CURRENT_DATE = datetime.date.today()
MONTH = CURRENT_DATE.month
YEAR = CURRENT_DATE.year
PREFIX = f"{str(MONTH).zfill(2)}-{YEAR}"
ISSUE_DATE_FORMATTED = CURRENT_DATE.strftime("%d de %B de %Y").capitalize()

# --- Folder Paths ---
INVOICES_FOLDER = "Invoices"
SUMMARIES_FOLDER = "Summaries"
INVOICE_SUBFOLDER = os.path.join(INVOICES_FOLDER, PREFIX)
LOGS_FOLDER = "logs"
AUTH_FOLDER = "auth"

# --- File Paths ---
STUDENTS_CSV_FILE = "students.csv"
NON_CLASS_DATES_FILE = "non_class_dates.txt"
CREDENTIALS_FILE = os.path.join(AUTH_FOLDER, "credentials.json")
# Separated token files for each service
SHEETS_TOKEN_FILE = os.path.join(AUTH_FOLDER, "gsheets/token.json")
DRIVE_TOKEN_FILE = os.path.join(AUTH_FOLDER, "gdrive/token.json")

# --- Asset Paths (new) ---
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
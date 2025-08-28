import argparse
import os
import datetime
from .preparation import download_sheet_data
from .schedule import process_data, save_csvs
from .image import generate_images
from .upload import upload_invoices
from . import config
from .utils import create_logging

# Configure logging for main.py
logger = create_logging(__name__, "main.log")


def parse_args():
    """
    Parses CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generate monthly invoices and summaries for English classes."
    )
    parser.add_argument(
        "-m", "--month", type=int, help="Month as MM (1–12). Defaults to current month."
    )
    parser.add_argument(
        "-y", "--year", type=int, help="Year as YYYY. Defaults to current year."
    )
    parser.add_argument(
        "-nd",
        "--non-class-dates",
        type=str,
        default=config.NON_CLASS_DATES_FILE,
        help="Path to a text file with manually specified non-class dates.",
    )
    return parser.parse_args()


def run_pipeline(month: int, year: int, non_class_dates_path: str):
    """
    Main pipeline function to orchestrate the entire process.
    """
    # Create dynamic variables based on the month and year
    prefix = f"{str(month).zfill(2)}-{year}"
    invoice_subfolder = os.path.join(config.INVOICES_FOLDER, prefix)

    # 1) Prepare folders
    os.makedirs(config.INVOICES_FOLDER, exist_ok=True)
    os.makedirs(config.SUMMARIES_FOLDER, exist_ok=True)
    os.makedirs(invoice_subfolder, exist_ok=True)

    # 2) Run pipeline
    print("⬇️ Downloading latest schedule data...")
    sheet_data = download_sheet_data()
    if not sheet_data:
        logger.warning("No data found in Google Sheet. Proceeding with local version.")
        students_csv_path = config.STUDENTS_CSV_FILE
    else:
        print(
            f"✅ Successfully downloaded data. Saving to '{config.STUDENTS_CSV_FILE}'."
        )
        with open(config.STUDENTS_CSV_FILE, "w", newline="") as csvfile:
            import csv

            writer = csv.writer(csvfile)
            writer.writerows(sheet_data)
        students_csv_path = config.STUDENTS_CSV_FILE

    print("📂 Creating data structure...")
    students_df, schedule_df = process_data(
        month, year, students_csv_path, non_class_dates_path
    )

    print("📄 Generating CSVs...")
    save_csvs(students_df, schedule_df, config.SUMMARIES_FOLDER, prefix)

    print("🖼️ Generating summary images...")
    generate_images(students_df, schedule_df, invoice_subfolder, prefix, month, year)

    print(
        f"✅ Done! CSVs in '{config.SUMMARIES_FOLDER}', images in '{invoice_subfolder}'.\n"
        f"   Files are prefixed with '{prefix}_'."
    )

    print("Uploading invoices to Google Drive...")
    upload_invoices(prefix)


def main():
    """
    Main entry point for the application.
    """
    args = parse_args()

    # Get current date as default
    today = datetime.date.today()
    month = args.month or today.month
    year = args.year or today.year
    non_class_dates_path = args.non_class_dates

    try:
        run_pipeline(month, year, non_class_dates_path)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()

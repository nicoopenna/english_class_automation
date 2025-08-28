import argparse
import os
import datetime
from preparation import download_sheet_data
from schedule import process_data, save_csvs
import image
import upload
import config
from utils import create_logging

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
    # 1) Prepare folders
    os.makedirs(config.INVOICES_FOLDER, exist_ok=True)
    os.makedirs(config.SUMMARIES_FOLDER, exist_ok=True)
    os.makedirs(config.INVOICE_SUBFOLDER, exist_ok=True)

    # 2) Run pipeline
    print("⬇️ Downloading latest schedule data...")
    sheet_data = download_sheet_data()
    if not sheet_data:
        logger.warning("No data found in Google Sheet. Proceeding with local version.")
        # Fallback to local data if no new data is downloaded
        # NOTE: This requires a pre-existing students.csv file
        students_csv_path = config.STUDENTS_CSV_FILE
    else:
        # If new data is downloaded, save it to the students.csv file
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
    save_csvs(students_df, schedule_df, config.SUMMARIES_FOLDER, config.PREFIX)

    print("🖼️ Generating summary images...")
    image.generate_images(
        students_df, schedule_df, config.INVOICE_SUBFOLDER, config.PREFIX
    )

    print(
        f"✅ Done! CSVs in '{config.SUMMARIES_FOLDER}', images in '{config.INVOICE_SUBFOLDER}'.\n"
        f"   Files are prefixed with '{config.PREFIX}_'."
    )

    print("Uploading invoices to Google Drive...")
    upload.upload_invoices(config.PREFIX)


def main():
    """
    Main entry point for the application.
    """
    args = parse_args()
    month = args.month or config.MONTH
    year = args.year or config.YEAR
    non_class_dates_path = args.non_class_dates
    try:
        run_pipeline(month, year, non_class_dates_path)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main()

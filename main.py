import argparse
import schedule
import image
import datetime
import os

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate monthly invoices and summaries for English classes."
    )
    parser.add_argument(
        "-m", "--month",
        type=int,
        help="Month as MM (1–12). Defaults to current month."
    )
    parser.add_argument(
        "-y", "--year",
        type=int,
        help="Year as YYYY. Defaults to current year."
    )
    return parser.parse_args()

def main():
    # 1) Parse CLI args (fall back to today’s month/year)
    args = parse_args()
    today = datetime.date.today()
    month = args.month or today.month
    year  = args.year  or today.year
    prefix = f"{str(month).zfill(2)}-{year}"

    # 2) Prepare folders
    INVOICES_FOLDER = "Invoices"
    SUMMARIES_FOLDER = "Summaries"
    invoice_subfolder = os.path.join(INVOICES_FOLDER, prefix)

    os.makedirs(invoice_subfolder, exist_ok=True)
    os.makedirs(SUMMARIES_FOLDER, exist_ok=True)

    # 3) Run pipeline
    print("📂 Creating data structure...")
    students_df, schedule_df = schedule.process_data(month, year)

    print("📄 Generating CSVs...")
    schedule.save_csvs(students_df, schedule_df, SUMMARIES_FOLDER, prefix)

    print("🖼️ Generating summary images...")
    image.generate_images(students_df, schedule_df, invoice_subfolder, prefix)

    print(
        f"✅ Done! CSVs in '{SUMMARIES_FOLDER}', images in '{invoice_subfolder}'.\n"
        f"   Files are prefixed with '{prefix}_'."
    )

if __name__ == "__main__":
    main()
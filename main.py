import schedule
import image
import datetime
import os

# Get the month-year prefix in numeric format (e.g., "06-2025")
month_year_prefix = datetime.date.today().strftime("%m-%Y")

# Define the folders (now constant names)
INVOICES_FOLDER = "Invoices"
SUMMARIES_FOLDER = "Summaries"

# Create folders if they don't exist
os.makedirs(INVOICES_FOLDER, exist_ok=True)
os.makedirs(SUMMARIES_FOLDER, exist_ok=True)

def main():
    print("📂 Creating data structure...")
    # Process the student and schedule data.
    students_df, schedule_df = schedule.process_data()

    print("📄 Generating CSVs...")
    schedule.save_csvs(students_df, schedule_df, SUMMARIES_FOLDER)

    print("🖼️ Generating summary images...")
    image.generate_images(students_df, schedule_df, INVOICES_FOLDER)

    print(f"✅ Process completed. CSV files are saved in '{SUMMARIES_FOLDER}' and images in '{INVOICES_FOLDER}', each prefixed with '{month_year_prefix}_'.")

if __name__ == "__main__":
    main()
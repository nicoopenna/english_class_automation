import pandas as pd
import requests
import datetime
import calendar
import locale
import os
from . import config
from typing import Set, List

# Set locale to Spanish for date formatting
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")


def get_holidays(year: int) -> Set[str]:
    """
    Retrieves holidays for the given year from the API.

    Parameters:
    - year (int): The target year.

    Returns:
    - Set[str]: A set of holiday dates in "YYYY-MM-DD" format.
    """
    try:
        response = requests.get(f"{config.HOLIDAYS_API_URL}{year}")
        response.raise_for_status()
        return {holiday["fecha"] for holiday in response.json()}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching holidays: {e}")
        return set()


def get_manual_non_class_dates(filepath: str) -> Set[str]:
    """
    Reads a text file with manually specified non-class dates.

    Parameters:
    - filepath (str): The path to the text file.

    Returns:
    - Set[str]: A set of dates to be excluded from the schedule.
    """
    non_class_dates = set()
    if not os.path.exists(filepath):
        print(f"⚠️ Manual non-class dates file not found at '{filepath}'.")
        return non_class_dates
    try:
        with open(filepath, "r") as file:
            for line in file:
                date_str = line.strip()
                if date_str:
                    try:
                        datetime.date.fromisoformat(date_str)
                        non_class_dates.add(date_str)
                    except ValueError:
                        print(
                            f"⚠️ Invalid date format '{date_str}' in file. Expected 'YYYY-MM-DD'."
                        )
        return non_class_dates
    except IOError as e:
        print(f"Error reading manual non-class dates file: {e}")
        return set()


def generate_class_dates(
    day_name: str, year: int, month: int, excluded_dates: Set[str]
) -> List[datetime.date]:
    """
    Generates all occurrences of a given weekday within the specified month,
    excluding holidays and manually specified dates.

    Parameters:
    - day_name (str): Day abbreviation ("Mon", "Tue", etc.) or full name ("Monday").
    - year (int): Target year.
    - month (int): Target month.
    - excluded_dates (set): A set of dates in "YYYY-MM-DD" format to be excluded.

    Returns:
    - list: datetime.date objects of valid class dates.
    """
    day_name = day_name.strip().title()
    weekday_map = {
        "Mon": 0,
        "Monday": 0,
        "Tue": 1,
        "Tuesday": 1,
        "Wed": 2,
        "Wednesday": 2,
        "Thu": 3,
        "Thursday": 3,
        "Fri": 4,
        "Friday": 4,
        "Sat": 5,
        "Saturday": 5,
        "Sun": 6,
        "Sunday": 6,
    }
    try:
        target_weekday = weekday_map[day_name]
    except KeyError:
        raise ValueError(f"Invalid day name: {day_name}")

    days_in_month = calendar.monthrange(year, month)[1]
    valid_dates = []

    for day in range(1, days_in_month + 1):
        date_obj = datetime.date(year, month, day)
        date_str = date_obj.strftime("%Y-%m-%d")
        if date_obj.weekday() == target_weekday and date_str not in excluded_dates:
            valid_dates.append(date_obj)

    return valid_dates


def process_data(
    month: int, year: int, students_csv_path: str, manual_dates_filepath: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Processes student data, calculates scheduled classes, and computes total hours and payment.

    Parameters:
    - month (int): The month for which to generate the schedule.
    - year (int): The year for which to generate the schedule.
    - students_csv_path (str): Path to the CSV file with student data.
    - manual_dates_filepath (str): Path to the file with manual non-class dates.

    Returns:
    - tuple[pd.DataFrame, pd.DataFrame]: A tuple containing the students summary DataFrame and the detailed schedule DataFrame.
    """
    try:
        students_df = pd.read_csv(students_csv_path)
    except FileNotFoundError:
        print(f"Error: '{students_csv_path}' not found. Please ensure it exists.")
        return pd.DataFrame(), pd.DataFrame()

    holidays = get_holidays(year)
    manual_non_class_dates = get_manual_non_class_dates(manual_dates_filepath)
    excluded_dates = holidays.union(manual_non_class_dates)

    all_class_data = []

    for _, row in students_df.iterrows():
        student_name = row["Student Name"]
        days = [d.strip() for d in row["Days Of Week"].split(",")]
        hours_per_day = list(map(float, row["Hours per Day"].split(",")))
        price_per_hour = float(row["Price per hour"])

        for day, hours in zip(days, hours_per_day):
            valid_dates = generate_class_dates(day, year, month, excluded_dates)
            for date_obj in valid_dates:
                all_class_data.append(
                    {
                        "Student": student_name,
                        "Date": date_obj,
                        "Hours": hours,
                        "Price per hour": price_per_hour,
                        "Day": date_obj.strftime("%a"),
                    }
                )

    schedule_df = pd.DataFrame(all_class_data)
    schedule_df["Date"] = pd.to_datetime(schedule_df["Date"])

    schedule_df["Payment"] = schedule_df["Hours"] * schedule_df["Price per hour"]

    students_summary_df = (
        schedule_df.groupby("Student")
        .agg(total_hours=("Hours", "sum"), total_payment=("Payment", "sum"))
        .reset_index()
    )

    students_df = pd.merge(
        students_df,
        students_summary_df,
        left_on="Student Name",
        right_on="Student",
        how="left",
    )

    students_df.rename(
        columns={"total_hours": "Total Hours", "total_payment": "Total Payment (ARS)"},
        inplace=True,
    )
    students_df.drop(columns="Student", inplace=True)
    students_df.fillna({"Total Hours": 0, "Total Payment (ARS)": 0}, inplace=True)

    schedule_df["Date"] = schedule_df["Date"].dt.strftime("%d-%B-%Y")
    schedule_df.drop(columns="Price per hour", inplace=True)

    return students_df, schedule_df


def save_csvs(
    students_df: pd.DataFrame,
    schedule_df: pd.DataFrame,
    summary_folder: str,
    prefix: str,
):
    """
    Saves DataFrames as CSVs.

    Parameters:
    - students_df (pd.DataFrame): DataFrame with student summaries.
    - schedule_df (pd.DataFrame): DataFrame with the detailed schedule.
    - summary_folder (str): Folder path to save the summary CSV.
    - prefix (str): Prefix for the output filenames.
    """
    os.makedirs(summary_folder, exist_ok=True)
    students_df.to_csv(f"{summary_folder}/{prefix}_summary.csv", index=False)
    schedule_df.to_csv(f"{summary_folder}/{prefix}_schedule.csv", index=False)

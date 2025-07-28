import pandas as pd
import requests
import datetime
import calendar
import locale
import os

# Set locale to Spanish for date formatting (output only)
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")  # For output formatting

API_URL = "https://api.argentinadatos.com/v1/feriados/"


def get_holidays(year):
    """Retrieves holidays for the given year from the API."""
    response = requests.get(f"{API_URL}{year}")
    if response.status_code == 200:
        return {holiday["fecha"] for holiday in response.json()}
    return set()


def generate_class_dates(day_name, year, month, holidays):
    """
    Generates all occurrences of a given weekday within the specified month (excluding holidays).

    Parameters:
    - day_name (str): Day abbreviation ("Mon", "Tue", etc.) or full name ("Monday")
    - year (int): Target year
    - month (int): Target month
    - holidays (set): Holiday dates in "YYYY-MM-DD" format

    Returns:
    - list: datetime.date objects of valid class dates
    """
    day_name = day_name.strip().title()  # Normalize input

    # Mapping for English day names
    weekday_map = {
        "Mon": 0, "Monday": 0,
        "Tue": 1, "Tuesday": 1,
        "Wed": 2, "Wednesday": 2,
        "Thu": 3, "Thursday": 3,
        "Fri": 4, "Friday": 4,
        "Sat": 5, "Saturday": 5,
        "Sun": 6, "Sunday": 6
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
        if date_obj.weekday() == target_weekday and date_str not in holidays:
            valid_dates.append(date_obj)

    return valid_dates


def process_data(month, year):
    """Processes student data with English day names."""
    students_df = pd.read_csv("students.csv")
    holidays = get_holidays(year)

    schedule_data = []
    for _, row in students_df.iterrows():
        student = row["Student Name"]
        days = [d.strip() for d in row["Days Of Week"].split(",")]
        hours_per_day = list(map(float, row["Hours per Day"].split(",")))
        price_per_hour = float(row["Price per hour"])

        total_hours = 0
        total_payment = 0

        for day, hours in zip(days, hours_per_day):
            valid_dates = generate_class_dates(day, year, month, holidays)
            for date_obj in valid_dates:
                formatted_date = date_obj.strftime("%d-%B-%Y")  # Spanish month names
                day_abbr = date_obj.strftime("%a")  # Spanish day abbrev (Lun, Mar)
                schedule_data.append({
                    "Student": student,
                    "Date": formatted_date,
                    "Hours": hours,
                    "Day": day_abbr
                })
                total_hours += hours
                total_payment += hours * price_per_hour

        students_df.loc[students_df["Student Name"] == student,
        ["Total Hours", "Total Payment (ARS)"]] = [total_hours, total_payment]

    return students_df, pd.DataFrame(schedule_data)


def save_csvs(students_df, schedule_df, summary_folder, prefix):
    """Saves DataFrames as CSVs (unchanged)."""
    os.makedirs(summary_folder, exist_ok=True)
    students_df.to_csv(f"{summary_folder}/{prefix}_summary.csv", index=False)
    schedule_df.to_csv(f"{summary_folder}/{prefix}_schedule.csv", index=False)
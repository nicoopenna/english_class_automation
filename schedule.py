import pandas as pd
import requests
import datetime
import calendar
import locale
import os

# Set locale to Spanish for proper date formatting
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")  # Alternatively, try "es_AR.UTF-8" if needed

API_URL = "https://api.argentinadatos.com/v1/feriados/"


def get_holidays(year):
    """
    Retrieves holidays for the given year from the API.
    Returns a set with dates in the format "YYYY-MM-DD".
    """
    response = requests.get(f"{API_URL}{year}")
    if response.status_code == 200:
        return {holiday["fecha"] for holiday in response.json()}
    return set()


def generate_class_dates(day_name, year, month, holidays):
    """
    Generates all occurrences of a given weekday within the specified month (excluding holidays).

    Parameters:
    - day_name (str): The day of the week, expected as an abbreviation (e.g., "Lun", "Mar", etc.).
                      Also accepts full names (e.g., "Lunes", "Martes", etc.) as a fallback.
    - year (int): Target year.
    - month (int): Target month.
    - holidays (set): A set of holiday dates in "YYYY-MM-DD" format.

    Returns:
    - A list of datetime.date objects representing valid class dates.
    """
    # Clean the input by removing extra whitespace.
    day_name = day_name.strip()

    # Mapping for abbreviation
    weekday_map = {"Lun": 0, "Mar": 1, "Mié": 2, "Mie": 2, "Jue": 3, "Vie": 4, "Sáb": 5, "Sab": 5, "Dom": 6}
    if day_name in weekday_map:
        target_weekday = weekday_map[day_name]
    else:
        # Fallback mapping for full day names in Spanish
        full_weekday_map = {"Lunes": 0, "Martes": 1, "Miércoles": 2, "Jueves": 3, "Viernes": 4, "Sábado": 5,
                            "Domingo": 6}
        target_weekday = full_weekday_map.get(day_name)
        if target_weekday is None:
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
    """
    Processes the student data, computes class dates, and calculates totals.

    Parameters:
    - month (int): Numeric month (e.g., 7 for July)
    - year (int): Four-digit year (e.g., 2025)

    Returns:
    Tuple: (students_df, schedule_df)
    """
    students_df = pd.read_csv("students.csv")
    holidays = get_holidays(year)

    schedule_data = []
    for _, row in students_df.iterrows():
        student = row["Student Name"]
        days = row["Days Of Week"].split(", ")
        hours_per_day = list(map(float, row["Hours per Day"].split(", ")))
        price_per_hour = float(row["Price per hour"])

        total_hours = 0
        total_payment = 0

        for day, hours in zip(days, hours_per_day):
            valid_dates = generate_class_dates(day, year, month, holidays)
            for date_obj in valid_dates:
                formatted_date = date_obj.strftime("%d-%B-%Y")
                day_abbr = date_obj.strftime("%a").title()
                schedule_data.append({
                    "Student": student,
                    "Date": formatted_date,
                    "Hours": hours,
                    "Day": day_abbr
                })
                total_hours += hours
                total_payment += hours * price_per_hour

        students_df.loc[students_df["Student Name"] == student, ["Total Hours", "Total Payment (ARS)"]] = [total_hours, total_payment]

    return students_df, pd.DataFrame(schedule_data)


def save_csvs(students_df, schedule_df, summary_folder, prefix):
    """
    Saves the students and schedule DataFrames as CSV files with a custom prefix.

    Parameters:
    - students_df (DataFrame): The processed student summary data.
    - schedule_df (DataFrame): The schedule data with dates and days.
    - summary_folder (str): Target folder for CSVs.
    - prefix (str): Custom month-year prefix like "07-2025".
    """
    os.makedirs(summary_folder, exist_ok=True)
    students_df.to_csv(f"{summary_folder}/{prefix}_summary.csv", index=False)
    schedule_df.to_csv(f"{summary_folder}/{prefix}_schedule.csv", index=False)
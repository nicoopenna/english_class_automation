from PIL import Image, ImageDraw, ImageFont
import os
import datetime
import locale

# Set locale to Spanish for proper month names
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")  # Try "es_AR.UTF-8" if needed

# Global settings
ISSUE_DATE = datetime.date.today().strftime("%d de %B de %Y").capitalize()
LOGO_PATH = "logo.png"  # Path to the logo image
FONT_BOLD = "arialbd.ttf"  # Bold font for section titles
FONT_REGULAR = "arial.ttf"  # Regular font for normal text


def generate_class_summary(student_name, class_days, total_hours, total_payment, invoice_folder):
    """
    Generates a structured class summary image for a given student and saves it.
    This version uses the adjusted formatting (everything moved upward by 50 units and no footer text)
    and the output filename is prefixed with the month-year in numeric format.

    Parameters:
    - student_name (str): Name of the student.
    - class_days (list): List of class dates (sorted chronologically, e.g., "05-Junio-2025").
    - total_hours (float): Total hours of classes.
    - total_payment (float): Total payment amount in ARS.
    - invoice_folder (str): Folder where the image will be saved.
    """
    # Create a blank image with white background
    img_width, img_height = 800, 1100
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    # Load fonts
    title_font = ImageFont.truetype(FONT_BOLD, 55)
    section_font = ImageFont.truetype(FONT_BOLD, 40)
    text_font = ImageFont.truetype(FONT_REGULAR, 35)

    # Insert the logo (larger and centered)
    logo = Image.open(LOGO_PATH).convert("RGBA")
    logo = logo.resize((220, 220))
    img.paste(logo, (290, 20), logo)

    # Center title text (moved upward by 50 pixels: y = 230 instead of 280)
    title_text = "RESUMEN DE CLASES"
    text_width = draw.textlength(title_text, font=title_font)
    center_x = (img_width - text_width) // 2
    draw.text((center_x, 230), title_text, font=title_font, fill="black")

    # Student Information (shifted upward by 50 pixels)
    draw.text((50, 320), f"Nombre: {student_name}", font=section_font, fill="black")
    draw.text((50, 380), f"Fecha de emisión: {ISSUE_DATE}", font=text_font, fill="black")

    # Separator line (moved upward)
    draw.line([(50, 420), (750, 420)], fill="black", width=3)

    # Class Schedule header
    draw.text((50, 450), "Días de Clase:", font=section_font, fill="black")

    # **Sort** the class days in chronological order
    class_days_sorted = sorted(class_days, key=lambda date: datetime.datetime.strptime(date, "%d-%B-%Y"))

    # **Split** class days into two columns if there are many entries
    split_index = len(class_days_sorted) // 2
    class_days_left = class_days_sorted[:split_index]
    class_days_right = class_days_sorted[split_index:]

    # Render first column of class days (starting at y = 500)
    y_offset_left = 500
    for day in class_days_left:
        draw.text((70, y_offset_left), f"- {day}", font=text_font, fill="black")
        y_offset_left += 45

    # Render second column (also starting at y = 500)
    y_offset_right = 500
    for day in class_days_right:
        draw.text((400, y_offset_right), f"- {day}", font=text_font, fill="black")
        y_offset_right += 45

    # Use the greater y-offset for the next section
    final_y = max(y_offset_left, y_offset_right)
    draw.line([(50, final_y + 20), (750, final_y + 20)], fill="black", width=3)

    # Display class hours and payment details (moved upward)
    draw.text((50, final_y + 50), f"Horas de Clase: {total_hours}", font=section_font, fill="black")
    draw.text((50, final_y + 100), f"Pago Total: ARS {total_payment}", font=section_font, fill="black")

    # Build the filename with the month-year prefix in numeric format (e.g., "06-2025")
    prefix = datetime.date.today().strftime("%m-%Y")
    filename = f"{prefix}_{student_name}_invoice.png"
    save_path = os.path.join(invoice_folder, filename)
    img.save(save_path)


def generate_images(students_df, schedule_df, invoice_folder):
    """
    Iterates over each student record and generates the invoice summary image.

    Parameters:
    - students_df (DataFrame): DataFrame containing student summary information.
    - schedule_df (DataFrame): DataFrame with the class schedule dates for each student.
    - invoice_folder (str): Folder where the invoice images will be saved.
    """
    for _, row in students_df.iterrows():
        student_name = row["Student Name"]
        total_hours = row["Total Hours"]
        total_payment = row["Total Payment (ARS)"]
        # Filter schedule_df by Student Name (the schedule CSV uses "Student" as the column key)
        student_class_days = schedule_df[schedule_df["Student"] == student_name]["Date"].tolist()
        generate_class_summary(student_name, student_class_days, total_hours, total_payment, invoice_folder)
from PIL import Image, ImageDraw, ImageFont
import os
import datetime
import locale
import math
import config

# Set locale to Spanish for proper month names
locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")


def generate_class_summary(
    student_name, class_days, total_hours, total_payment, invoice_folder, prefix
):
    """
    Generates a structured class summary image for a given student and saves it.
    Splits class days into three columns and formats dates as "DD/MM/YYYY".
    """
    # Canvas setup
    img_width, img_height = 800, 1100
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    # Load fonts
    title_font = ImageFont.truetype(config.FONT_BOLD, 55)
    section_font = ImageFont.truetype(config.FONT_BOLD, 40)
    text_font = ImageFont.truetype(config.FONT_REGULAR, 35)

    # Logo & title
    logo = Image.open(config.LOGO_PATH).convert("RGBA").resize((220, 220))
    img.paste(logo, (290, 20), logo)
    title_text = "RESUMEN DE CLASES"
    tw = draw.textlength(title_text, font=title_font)
    draw.text(((img_width - tw) // 2, 230), title_text, font=title_font, fill="black")

    # Student info
    draw.text((50, 320), f"Nombre: {student_name}", font=section_font, fill="black")
    draw.text(
        (50, 380),
        f"Fecha de emisión: {config.ISSUE_DATE_FORMATTED}",
        font=text_font,
        fill="black",
    )
    draw.line([(50, 420), (750, 420)], fill="black", width=3)
    draw.text((50, 450), "Días de Clase:", font=section_font, fill="black")

    # Parse, sort & format dates
    parsed = [datetime.datetime.strptime(d, "%d-%B-%Y") for d in class_days]
    parsed.sort()
    formatted = [dt.strftime("%d/%m/%Y") for dt in parsed]

    # Split into 3 columns
    n = len(formatted)
    per_col = math.ceil(n / 3)
    cols = [
        formatted[0:per_col],
        formatted[per_col : per_col * 2],
        formatted[per_col * 2 : per_col * 3],
    ]
    while len(cols) < 3:
        cols.append([])

    # Render columns
    x_positions = [70, 300, 530]
    y_start = 500
    y_ends = []
    for i, col in enumerate(cols):
        x = x_positions[i]
        y = y_start
        for day in col:
            draw.text((x, y), f"- {day}", font=text_font, fill="black")
            y += 45
        y_ends.append(y)

    # Footer line & totals
    final_y = max(y_ends)
    draw.line([(50, final_y + 20), (750, final_y + 20)], fill="black", width=3)
    draw.text(
        (50, final_y + 50),
        f"Horas de Clase: {total_hours}",
        font=section_font,
        fill="black",
    )
    draw.text(
        (50, final_y + 100),
        f"Pago Total: ARS {total_payment}",
        font=section_font,
        fill="black",
    )

    # Save file
    safe_name = "".join(c if c.isalnum() else "_" for c in student_name)
    filename = f"{prefix}_{safe_name}_invoice.png"
    img.save(os.path.join(invoice_folder, filename))


def generate_images(students_df, schedule_df, invoice_folder, prefix):
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
        student_class_days = schedule_df[schedule_df["Student"] == student_name][
            "Date"
        ].tolist()
        generate_class_summary(
            student_name,
            student_class_days,
            total_hours,
            total_payment,
            invoice_folder,
            prefix,
        )

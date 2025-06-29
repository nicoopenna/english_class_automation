# English Classes Invoice Generator

**Tags:** `Python` `pandas` `Pillow` `argparse` `locale`

Automate monthly CSV summaries and per-student invoice PNGs for your English tutoring.

## 🚀 Features
- Reads `students.csv`, computes class dates (skips holidays)  
- Exports:
  - `Summaries/<MM-YYYY>_summary.csv` (totals)
  - `Summaries/<MM-YYYY>_schedule.csv` (per-class dates)
  - `Invoices/<MM-YYYY>/<MM-YYYY_Student_invoice.png>`
- CLI flags `--month` & `--year` (defaults to today)  
- Three-column date layout

## 🔧 Requirements
- Python 3.8+  
- pandas, Pillow (`pip install -r requirements.txt`)  
- Spanish locale (e.g. `es_ES.UTF-8`)  
- Fonts: `arial.ttf`, `arialbd.ttf`  

## ⚙️ Quickstart
```bash
git clone <repo> && cd <repo>
pip install -r requirements.txt
# add logo.png & students.csv
python main.py --month 7 --year 2025
# English Class Automation System

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Google APIs](https://img.shields.io/badge/Google%20Sheets%20API-✓-green.svg)
![Google Drive](https://img.shields.io/badge/Google%20Drive%20API-✓-green.svg)
![Automation](https://img.shields.io/badge/automation-✓-brightgreen.svg)

## 🌟 Features

### Data Pipeline
- Dynamic CSV export from Google Sheets
- Holiday-aware scheduling
- Bilingual date handling (English/Spanish)

### Google Drive Integration
- OAuth2 authenticated uploads
- Automatic month/year folder creation
- Conflict-resistant file management

### Invoice Generation
- PDF creation with professional typography
- Automatic totals calculation
- Clean template design

## 🛠 Tech Stack

```mermaid
graph LR
    A[Sheets] --> B[Python]
    B --> C[PNGs]
    B --> D[Drive]
```
# 🚀 Usage
## Run with specific month/year
```shell
python main.py -m 8 -y 2025
```
### Auto-detect current month
```shell
python main.py
```


## 📂 File Structure
/ (root)
├── Invoices/           # Generated PNGs
├── logs/               # Execution logs
├── auth/               # OAuth credentials
├── main.py             # Core pipeline
├── preparation.py      # Sheets exporter
└── upload.py           # Drive uploader
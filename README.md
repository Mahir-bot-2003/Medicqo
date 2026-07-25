# Medicqo — Hospital CRM & Digital Prescriptions

A comprehensive, Python-based Hospital CRM and Digital Prescription generator. This system allows doctors to authenticate, manage their patient roster, instantly generate PDF prescriptions, and securely transmit them directly to patients via WhatsApp or Telegram.

## Features

- **Doctor Registration & Authentication**: Secure login flow allowing multiple doctors to manage their own patients.
- **Patient Management**: Add new patients, search through existing records, and easily delete patients.
- **Digital Prescriptions**: Create detailed prescriptions with patient symptoms, diagnoses, notes, and a structured list of medicines (including dosage, frequency, and duration).
- **Automated PDF Generation**: Instantly compiles prescription data into a clean, professional PDF file using `reportlab`.
- **Direct Messaging Integration**:
  - **WhatsApp**: Seamlessly converts the PDF to a high-quality image on the backend (using `PyMuPDF`) and delivers it directly to the patient's WhatsApp using Twilio.
  - **Telegram**: Sends the raw PDF document securely to the patient's Telegram chat via a Telegram Bot.
- **Modern Desktop UI**: A beautiful, responsive desktop application built with `CustomTkinter`.

## Tech Stack

- **Backend API**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend App**: CustomTkinter (Python Desktop GUI)
- **PDF Generation**: ReportLab
- **Messaging Services**: Twilio API (WhatsApp) & python-telegram-bot
- **PDF Processing**: PyMuPDF (fitz)

## Prerequisites

- Python 3.10+
- A Twilio Account (for WhatsApp integration)
- A Telegram Bot Token (for Telegram integration)

## Installation & Setup

1. **Clone the repository** (or download the source code).
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn sqlalchemy httpx customtkinter reportlab python-telegram-bot twilio PyMuPDF
   ```

## Running the Application

This system is decoupled into a robust Backend API and a Desktop Frontend. You must run both.

**1. Start the Backend API**
Open a terminal, activate your virtual environment, and run:
```bash
uvicorn backend.main:app --reload
```
*The API will start at http://127.0.0.1:8000*

**2. Generate Demo Data (Optional)**
To easily populate your database with a default doctor ("Dr. Nav S") and two sample patients, run:
```bash
python create_demo_data.py
```

**3. Launch the Desktop App**
Open a **new** terminal window, activate your virtual environment, and run:
```bash
python frontend/app.py
```

## Configuration

To enable the messaging features, you must supply your API keys inside the backend messaging controller (`backend/messaging.py` or `backend/main.py`).

- **WhatsApp (Twilio)**: Replace the placeholder `account_sid` and `auth_token` in `backend/main.py` with your Twilio API credentials. Ensure the Twilio Sandbox is active and configured correctly.
- **Telegram**: Replace the placeholder `bot_token` in `backend/main.py` with the token provided by the BotFather on Telegram.

## Project Structure

```
├── backend/
│   ├── main.py         # FastAPI application and routing
│   ├── models.py       # SQLAlchemy database models
│   ├── schemas.py      # Pydantic validation schemas
│   ├── crud.py         # Database query wrappers
│   ├── database.py     # SQLite connection setup
│   ├── pdf_gen.py      # ReportLab PDF generation logic
│   └── messaging.py    # Twilio and Telegram API classes
├── frontend/
│   └── app.py          # CustomTkinter Desktop UI
├── create_demo_data.py # Script to populate initial DB state
└── README.md           # This file
```

## Future Scope

- **Cloud Database Migration**: Support for PostgreSQL/MySQL for multi-clinic synchronization across locations.
- **AI-Assisted Diagnostics**: Integration with LLMs/AI models to suggest diagnoses and flag potential drug-to-drug interaction warnings.
- **Patient Mobile App & Portal**: Dedicated patient dashboard to view medical history, follow-up dates, and download past PDF prescriptions.
- **Pharmacy & Inventory Integration**: Automatic stock deduction upon prescription generation and low-inventory alerts for clinics.
- **Billing & Invoicing Module**: Integrated payment gateways and automated invoice generation for consultation and treatment fees.
- **Digital Signatures & FHIR/HL7 Compliance**: Secure digital signature verification for legal e-prescriptions adhering to international healthcare standards.

---
*Built as a state-of-the-art Digital Hospital CRM Demonstration.*

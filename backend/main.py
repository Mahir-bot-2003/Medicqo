from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os
import json

from . import crud, models, schemas, pdf_gen, messaging
from .database import engine, get_db

# Create DB tables
models.Base.metadata.create_all(bind=engine)

SETTINGS_FILE = "settings.json"

def get_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "twilio_sid": "",
            "twilio_auth": "",
            "twilio_from": "",
            "telegram_bot_token": ""
        }
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

app = FastAPI(title="Digital Prescription System Demo API")

@app.get("/settings/")
def read_settings():
    return get_settings()

from fastapi import Body

@app.post("/settings/")
def update_settings(settings: dict = Body(...)):
    import json
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)
    return {"message": "Settings saved"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("prescriptions_pdfs"):
    os.makedirs("prescriptions_pdfs")
app.mount("/pdfs", StaticFiles(directory="prescriptions_pdfs"), name="pdfs")

@app.get("/")
def read_root():
    return {"message": "Welcome to Digital Prescription API"}

# --- Patients ---
@app.post("/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    db_patient = crud.get_patient_by_phone(db, phone=patient.phone)
    if db_patient:
        raise HTTPException(status_code=400, detail="Phone already registered")
    return crud.create_patient(db=db, patient=patient)

@app.get("/patients/", response_model=List[schemas.Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    patients = crud.get_patients(db, skip=skip, limit=limit)
    return patients

@app.get("/patients/search/", response_model=List[schemas.Patient])
def search_patients(q: str, db: Session = Depends(get_db)):
    patients = crud.search_patients(db, query=q)
    return patients

@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    crud.delete_patient(db, patient_id=patient_id)
    return {"message": "Patient deleted successfully"}

# --- Prescriptions ---
@app.post("/prescriptions/", response_model=schemas.Prescription)
def create_prescription(
    prescription: schemas.PrescriptionCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Verify patient exists
    db_patient = crud.get_patient(db, patient_id=prescription.patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Verify doctor exists
    db_doctor = crud.get_doctor(db, doctor_id=prescription.doctor_id)
    if not db_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    created_prescription = crud.create_prescription(db=db, prescription=prescription)
    
    # We will trigger PDF generation and messaging as a background task
    background_tasks.add_task(process_prescription_after_create, created_prescription.id, db_patient.id, db_doctor.id, prescription.send_channel)
    
    return created_prescription

def process_prescription_after_create(prescription_id: int, patient_id: int, doctor_id: int, send_channel: str):
    # This runs in a background thread, so we need a new DB session
    db = next(get_db())
    try:
        prescription = crud.get_prescriptions_by_patient(db, patient_id)[0] # Assuming it's the latest
        patient = crud.get_patient(db, patient_id)
        doctor = crud.get_doctor(db, doctor_id)
        
        # 1. Generate PDF
        pdf_path = pdf_gen.generate_prescription_pdf(prescription, patient, doctor)
        crud.update_prescription_pdf(db, prescription_id, pdf_path)
        
        # 2. Send Message (Skip if preview)
        if send_channel == "preview":
            return
            
        settings = get_settings()
        if send_channel == "whatsapp":
            channel = messaging.WhatsAppTwilioChannel(
                account_sid=settings.get("twilio_sid", ""),
                auth_token=settings.get("twilio_auth", ""),
                from_number=settings.get("twilio_from", "")
            )
        else:
            channel = messaging.TelegramChannel(bot_token=settings.get("telegram_bot_token", ""))
            
        result = channel.send_prescription(patient.phone, pdf_path, patient.name)
        
        # 3. Log Message
        msg_log = schemas.MessageLogCreate(
            prescription_id=prescription_id,
            channel=send_channel,
            status="sent" if result.success else "failed",
            error_message=result.error_message
        )
        # Note: We should probably create a crud function for message_log, for now doing it manually here or adding one
    finally:
        db.close()

@app.get("/patients/{patient_id}/prescriptions/", response_model=List[schemas.Prescription])
def read_prescriptions_for_patient(patient_id: int, db: Session = Depends(get_db)):
    prescriptions = crud.get_prescriptions_by_patient(db, patient_id=patient_id)
    return prescriptions

# --- Doctors ---
@app.post("/doctors/", response_model=schemas.Doctor)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    return crud.create_doctor(db=db, doctor=doctor)

@app.get("/doctors/{doctor_id}", response_model=schemas.Doctor)
def read_doctor(doctor_id: int, db: Session = Depends(get_db)):
    db_doctor = crud.get_doctor(db, doctor_id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@app.post("/doctors/login", response_model=schemas.Doctor)
def login_doctor(login_data: schemas.DoctorLogin, db: Session = Depends(get_db)):
    doctor = crud.authenticate_doctor(db, login_data.phone, login_data.password)
    if not doctor:
        raise HTTPException(status_code=401, detail="Invalid phone number or password")
    return doctor

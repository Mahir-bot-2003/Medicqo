from sqlalchemy.orm import Session
from . import models, schemas

# --- Patients ---
def get_patient(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patient_by_phone(db: Session, phone: str):
    return db.query(models.Patient).filter(models.Patient.phone == phone).first()

def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Patient).offset(skip).limit(limit).all()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(
        name=patient.name,
        phone=patient.phone,
        dob=patient.dob,
        gender=patient.gender
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    # This will also delete related prescriptions due to cascade in models (if configured)
    # SQLite often requires PRAGMA foreign_keys=ON or manual deletion.
    # We will manually delete prescriptions first to be safe.
    db.query(models.Prescription).filter(models.Prescription.patient_id == patient_id).delete()
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if db_patient:
        db.delete(db_patient)
        db.commit()
    return db_patient

def search_patients(db: Session, query: str):
    return db.query(models.Patient).filter(
        (models.Patient.name.ilike(f"%{query}%")) | 
        (models.Patient.phone.ilike(f"%{query}%"))
    ).all()


# --- Prescriptions ---
def create_prescription(db: Session, prescription: schemas.PrescriptionCreate):
    # Convert list of pydantic models to list of dicts for JSON column
    prescription_data = prescription.dict()
    # Remove send_channel because it's not a column in the Prescription model
    prescription_data.pop("send_channel", None)
    
    db_prescription = models.Prescription(**prescription_data)
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

def get_prescriptions_by_patient(db: Session, patient_id: int):
    return db.query(models.Prescription).filter(
        models.Prescription.patient_id == patient_id
    ).order_by(models.Prescription.created_at.desc()).all()

def update_prescription_pdf(db: Session, prescription_id: int, pdf_url: str):
    db_prescription = db.query(models.Prescription).filter(models.Prescription.id == prescription_id).first()
    if db_prescription:
        db_prescription.pdf_url = pdf_url
        db.commit()
        db.refresh(db_prescription)
    return db_prescription


# --- Doctors ---
def get_doctor(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()

def create_doctor(db: Session, doctor: schemas.DoctorCreate):
    # In a real app, hash the password
    fake_hashed_password = doctor.password + "notreallyhashed"
    db_doctor = models.Doctor(
        name=doctor.name,
        specialization=doctor.specialization,
        phone=doctor.phone,
        hashed_password=fake_hashed_password
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def authenticate_doctor(db: Session, phone: str, password: str):
    db_doctor = db.query(models.Doctor).filter(models.Doctor.phone == phone).first()
    if not db_doctor:
        return None
    fake_hashed_password = password + "notreallyhashed"
    if db_doctor.hashed_password == fake_hashed_password:
        return db_doctor
    return None

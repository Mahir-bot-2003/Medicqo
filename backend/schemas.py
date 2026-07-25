from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

# --- Medicines ---
class MedicineItem(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str

# --- Patients ---
class PatientBase(BaseModel):
    name: str
    phone: str
    dob: str
    gender: str

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int

    class Config:
        orm_mode = True

# --- Prescriptions ---
class PrescriptionBase(BaseModel):
    symptoms: str
    diagnosis: str
    notes: Optional[str] = None
    medicines: List[MedicineItem]

class PrescriptionCreate(PrescriptionBase):
    patient_id: int
    doctor_id: int
    send_channel: str = "telegram"

class Prescription(PrescriptionBase):
    id: int
    patient_id: int
    doctor_id: int
    created_at: datetime
    pdf_url: Optional[str] = None

    class Config:
        orm_mode = True

# --- Doctors ---
class DoctorBase(BaseModel):
    name: str
    specialization: str
    phone: str

class DoctorCreate(DoctorBase):
    password: str

class DoctorLogin(BaseModel):
    phone: str
    password: str

class Doctor(DoctorBase):
    id: int

    class Config:
        orm_mode = True

# --- Messages ---
class MessageLogBase(BaseModel):
    channel: str
    status: str
    error_message: Optional[str] = None

class MessageLogCreate(MessageLogBase):
    prescription_id: int

class MessageLog(MessageLogBase):
    id: int
    prescription_id: int
    sent_at: datetime

    class Config:
        orm_mode = True

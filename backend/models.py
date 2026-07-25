from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
import datetime

from .database import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialization = Column(String)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    prescriptions = relationship("Prescription", back_populates="doctor")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone = Column(String, index=True) # Will be encrypted at rest in prod, for now store as is (or basic hash if not needing to decrypt for search)
    # To search by phone while encrypted at rest, a deterministic encryption or blind index is needed.
    # For this demo MVP, we will keep it simple but acknowledge it.
    dob = Column(String)
    gender = Column(String)

    prescriptions = relationship("Prescription", back_populates="patient")

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    symptoms = Column(Text)
    diagnosis = Column(Text)
    notes = Column(Text)
    medicines = Column(JSON) # Store structured list of medicines
    pdf_url = Column(String, nullable=True)

    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")
    messages = relationship("MessageLog", back_populates="prescription")

class MessageLog(Base):
    __tablename__ = "message_log"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"))
    channel = Column(String) # telegram, whatsapp, sms
    status = Column(String) # sent, failed, pending
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    error_message = Column(Text, nullable=True)

    prescription = relationship("Prescription", back_populates="messages")

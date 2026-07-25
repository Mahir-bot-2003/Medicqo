import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from . import schemas

PDF_DIR = "./prescriptions_pdfs"
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

def generate_prescription_pdf(prescription: schemas.Prescription, patient: schemas.Patient, doctor: schemas.Doctor) -> str:
    filename = f"prescription_{prescription.id}.pdf"
    filepath = os.path.join(PDF_DIR, filename)

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1 * inch, height - 1 * inch, "DIGITAL PRESCRIPTION")
    
    # Doctor Details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, height - 1.5 * inch, f"Dr. {doctor.name}")
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, height - 1.7 * inch, f"{doctor.specialization}")
    c.drawString(1 * inch, height - 1.9 * inch, f"Phone: {doctor.phone}")

    # Patient Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(5 * inch, height - 1.5 * inch, "Patient Details:")
    c.setFont("Helvetica", 12)
    c.drawString(5 * inch, height - 1.7 * inch, f"Name: {patient.name}")
    c.drawString(5 * inch, height - 1.9 * inch, f"Gender/DOB: {patient.gender}, {patient.dob}")
    c.drawString(5 * inch, height - 2.1 * inch, f"Date: {prescription.created_at.strftime('%Y-%m-%d')}")

    # Line Separator
    c.line(1 * inch, height - 2.3 * inch, width - 1 * inch, height - 2.3 * inch)

    # Diagnosis & Symptoms
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 2.6 * inch, "Symptoms:")
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, height - 2.8 * inch, prescription.symptoms)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(1 * inch, height - 3.2 * inch, "Diagnosis:")
    c.setFont("Helvetica", 12)
    c.drawString(1 * inch, height - 3.4 * inch, prescription.diagnosis)

    # Medicines
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, height - 4.0 * inch, "Rx (Medicines):")
    
    y_pos = height - 4.3 * inch
    c.setFont("Helvetica", 12)
    for i, med in enumerate(prescription.medicines):
        c.drawString(1 * inch, y_pos, f"{i+1}. {med['name']} - {med['dosage']}")
        c.drawString(1.2 * inch, y_pos - 0.2 * inch, f"Freq: {med['frequency']} | Duration: {med['duration']}")
        y_pos -= 0.5 * inch

    # Notes
    if prescription.notes:
        y_pos -= 0.3 * inch
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, y_pos, "Additional Notes:")
        c.setFont("Helvetica", 12)
        c.drawString(1 * inch, y_pos - 0.2 * inch, prescription.notes)

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(1 * inch, 1 * inch, "This is a computer generated digital prescription.")

    c.save()
    return filepath

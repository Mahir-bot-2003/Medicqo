import httpx

API_URL = "http://127.0.0.1:8000"

def setup():
    try:
        # Create doctor
        res = httpx.post(f"{API_URL}/doctors/", json={
            "name": "Nav S",
            "specialization": "General Physician",
            "phone": "555-0100",
            "password": "demo"
        })
        print("Doctor setup:", res.json())

        # Create some patients
        patients = [
            {"name": "Alice Johnson", "phone": "1234567890", "dob": "1980-05-15", "gender": "Female"},
            {"name": "Bob Williams", "phone": "0987654321", "dob": "1992-11-20", "gender": "Male"}
        ]
        
        for p in patients:
            res = httpx.post(f"{API_URL}/patients/", json=p)
            print("Patient setup:", res.json())
            
    except Exception as e:
        print("Error connecting to API:", e)

if __name__ == "__main__":
    setup()

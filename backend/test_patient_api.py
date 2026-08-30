# Test patient API routes in isolation
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.database import init_db
from app.routes.patient_routes import router

# Initialize database
init_db()

# Create app with just patient router
app = FastAPI()
app.include_router(router, prefix="/api/patients", tags=["Patients"])

client = TestClient(app)

print("Testing patient routes...")

# Test listing patients (should return existing patients)
resp = client.get("/api/patients")
print("GET /api/patients:", resp.status_code)
if resp.status_code == 200:
    data = resp.json()
    print("Patients count:", len(data))
    for p in data:
        print(" -", p.get("full_name"), p.get("patient_ref"))
else:
    print("Error body:", resp.text)

# Test creating a patient
resp = client.post("/api/patients", json={
    "full_name": "vishwa",
    "age": 20,
    "sex": "Male",
    "medical_history": "",
    "allergies": "",
    "medications": "",
    "previous_endoscopy": "",
    "family_history": ""
})
print("POST /api/patients (vishwa):", resp.status_code)
if resp.status_code in [200, 201]:
    data = resp.json()
    print("Created patient:", data.get("full_name"), data.get("patient_ref"), data.get("id"))
    print("Response fields:", list(data.keys()))
else:
    print("Error body:", resp.text)

# Test creating another patient
resp2 = client.post("/api/patients", json={
    "full_name": "john doe",
    "age": 30,
    "sex": "Female",
    "medical_history": "",
    "allergies": "",
    "medications": "",
    "previous_endoscopy": "",
    "family_history": ""
})
print("POST /api/patients (john doe):", resp2.status_code)
if resp2.status_code in [200, 201]:
    data = resp2.json()
    print("Created patient:", data.get("full_name"), data.get("patient_ref"), data.get("id"))
else:
    print("Error body:", resp2.text)
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Patient, Prediction, Base
from app.routes.patient_routes import get_patient, get_patient_predictions
from app.routes.analysis_routes import analyze
import json

client = TestClient(app)

# Test 1: Health endpoint
r = client.get('/health')
s = 'PASS' if r.status_code == 200 else 'FAIL'
print(f'1. GET /health: {r.status_code} {s}')

# Test 2: Auth me without token
r = client.get('/api/auth/me')
s = 'PASS' if r.status_code == 401 else 'FAIL'
print(f'2. GET /api/auth/me (no token): {r.status_code} {s}')

# Test 3: Patients without token
r = client.get('/api/patients')
s = 'PASS' if r.status_code == 200 else 'FAIL'
print(f'3. GET /api/patients (no token): {r.status_code} ({len(r.json())} patients) {s}')

# Test 4: Check patient routes import works
try:
    from app.routes.patient_routes import router as patient_router
    print(f'4. patient_routes imported: PASS')
except Exception as e:
    print(f'4. patient_routes import FAIL: {e}')

# Test 5: Check analysis routes import works
try:
    from app.routes.analysis_routes import router as analysis_router
    print(f'5. analysis_routes imported: PASS')
except Exception as e:
    print(f'5. analysis_routes import FAIL: {e}')

# Test 6: Create patient and test predictions
token = 'dummy'
r = client.post('/api/auth/signup', json={
    'full_name': 'Test User',
    'email': 'testuser3@example.com',
    'password': 'Testpass123',
    'confirm_password': 'Testpass123'
})
if r.status_code in [200, 201]:
    login_r = client.post('/api/auth/login', json={
        'email': 'testuser3@example.com',
        'password': 'Testpass123'
    })
    if login_r.status_code == 200:
        token = login_r.json()['access_token']
        # Create patient
        p = client.post('/api/patients', json={
            'full_name': 'Test Patient',
            'age': 35,
            'sex': 'Male',
            'medical_history': 'None',
            'allergies': 'None',
            'medications': 'None',
            'previous_endoscopy': 'None',
            'family_history': 'None'
        }, headers={'Authorization': f'Bearer {token}'})
        if p.status_code == 201:
            patient = p.json()
            patient_ref = patient['patient_ref']
            print(f'6. Created patient: {patient_ref}')
            
            # Test predictions endpoint
            r5 = client.get(f'/api/patients/{patient_ref}/predictions', 
                          headers={'Authorization': f'Bearer {token}'})
            s = 'PASS' if r5.status_code in [200, 404] else 'FAIL'
            print(f'7. GET /api/patients/{patient_ref}/predictions: {r5.status_code} {s}')
            if r5.status_code == 200:
                print(f'   Predictions: {r5.json()}')
            elif r5.status_code == 404:
                print(f'   404 (expected - no predictions yet)')

print('\nAll checks complete.')
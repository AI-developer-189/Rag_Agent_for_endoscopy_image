from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

# Test health
r = client.get('/health')
print(f'GET /health: {r.status_code} {r.json()}')

# Test auth me (no auth)
r = client.get('/api/auth/me')
print(f'GET /api/auth/me (no auth): {r.status_code}')

# Test patients (no auth)
r = client.get('/api/patients')
print(f'GET /api/patients (no auth): {r.status_code} {r.json()}')

# Test signup
r = client.post('/api/auth/signup', json={
    'full_name': 'Test User',
    'email': 'testuser2@example.com',
    'password': 'Testpass123',
    'confirm_password': 'Testpass123'
})
print(f'POST /api/auth/signup: {r.status_code}')
if r.status_code in [200, 201]:
    print(f'  Response: {r.json()}')

# Test login
r = client.post('/api/auth/login', json={
    'email': 'testuser2@example.com',
    'password': 'Testpass123'
})
print(f'POST /api/auth/login: {r.status_code}')
if r.status_code == 200:
    token = r.json()['access_token']
    print(f'  Token: {token[:20]}...')
    
    # Test auth me with token
    r2 = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    print(f'GET /api/auth/me with token: {r2.status_code} {r2.json()}')
    
    # Test patients with token
    r3 = client.get('/api/patients', headers={'Authorization': f'Bearer {token}'})
    print(f'GET /api/patients with token: {r3.status_code} {r3.json()}')
    
    # Test create patient
    r4 = client.post('/api/patients', json={
        'full_name': 'Test Patient',
        'age': 35,
        'sex': 'Male',
        'medical_history': 'None',
        'allergies': 'None',
        'medications': 'None',
        'previous_endoscopy': 'None',
        'family_history': 'None'
    }, headers={'Authorization': f'Bearer {token}'})
    print(f'POST /api/patients: {r4.status_code}')
    if r4.status_code == 201:
        patient = r4.json()
        patient_ref = patient['patient_ref']
        print(f'  Patient ref: {patient_ref}')
        print(f'  Full name: {patient["full_name"]}')
        
        # Test predictions endpoint with patient_ref
        print(f'GET /api/patients/{patient_ref}/predictions: ', end='')
        r5 = client.get(f'/api/patients/{patient_ref}/predictions', headers={'Authorization': f'Bearer {token}'})
        print(f'{r5.status_code}', end='')
        if r5.status_code == 200:
            print(f' {r5.json()}')
        elif r5.status_code == 404:
            print(' 404 (expected - no predictions)')
        else:
            print(f' {r5.text}')
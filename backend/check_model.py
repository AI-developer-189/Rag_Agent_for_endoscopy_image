from app.database import Base, Patient, Study, Prediction
from sqlalchemy import inspect
import sqlite3

# Check the model columns
print('Patient model id column:', Patient.id.columns.keys())
print('Patient id type:', type(Patient.id.type).__name__)
print('Patient id primary_key:', Patient.id.primary_key)

# Try to reflect the existing database
conn = sqlite3.connect('endoscopy.db')
c = conn.cursor()
c.execute('PRAGMA table_info(patients)')
db_cols = {r[1]: r[2] for r in c.fetchall()}
print('DB patients id type:', db_cols.get('id', 'NOT FOUND'))
conn.close()
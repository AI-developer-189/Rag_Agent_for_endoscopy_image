import sqlite3
import os

# Verify the final database state
db_path = r'F:\Multimodel\endoscopy.db'
if not os.path.exists(db_path):
    print('DB not found at', db_path)
    exit(1)

conn = sqlite3.connect(db_path)

# Check patients table schema
print('=== PRAGMA table_info(patients) ===')
columns = conn.execute('PRAGMA table_info(patients)').fetchall()
for col in columns:
    print(f'  {col}')

print()
print('=== Patients data ===')
patients = conn.execute('SELECT id, patient_ref, full_name, age, sex, created_at, updated_at FROM patients').fetchall()
for p in patients:
    print(f'  {p}')

print()
print('=== Check for obsolete name column ===')
has_name = any(c[1] == 'name' for c in columns)
if has_name:
    print('ERROR: name column still exists!')
else:
    print('OK: name column has been removed')

print()
print('=== Check full_name NOT NULL ===')
fn_col = [c for c in columns if c[1] == 'full_name'][0]
print(f'full_name notnull={fn_col[3]} (1=NOT NULL, 0=nullable)')

print()
print('=== Check sex NOT NULL ===')
sex_col = [c for c in columns if c[1] == 'sex'][0]
print(f'sex notnull={sex_col[3]} (1=NOT NULL, 0=nullable)')

conn.close()
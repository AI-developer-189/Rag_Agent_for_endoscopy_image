import sqlite3

conn = sqlite3.connect('endoscopy.db')
tables = conn.execute("SELECT * FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', tables)

cols = conn.execute('PRAGMA table_info(patients)').fetchall()
print('Patient columns:')
for col in cols:
    print(' ', col)

patients = conn.execute('SELECT * FROM patients').fetchall()
print(f'Patients ({len(patients)}):')
for p in patients:
    print(' ', p)

conn.close()
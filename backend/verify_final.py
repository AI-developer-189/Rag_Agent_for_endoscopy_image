import sqlite3
conn = sqlite3.connect('endoscopy.db')
c = conn.execute('PRAGMA table_info(patients)').fetchall()
print('Patient columns:')
for col in c:
    print(' ', c)
c = conn.execute('SELECT * FROM patients').fetchall()
print('Patients:')
for p in c:
    print(' ', p)
conn.close()
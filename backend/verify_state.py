import sqlite3
conn = sqlite3.connect('endoscopy.db')
c = conn.execute('PRAGMA table_info(patients)').fetchall()
print('Patient columns after migration:')
for col in c:
    print(' ', col)
print()
c = conn.execute('SELECT * FROM patients').fetchall()
print('Patients after migration:')
for p in c:
    print(' ', p)
conn.close()
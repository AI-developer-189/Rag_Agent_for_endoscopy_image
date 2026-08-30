import sqlite3
conn = sqlite3.connect('endoscopy.db')
c = conn.execute("SELECT * FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', c)
if 'patients' in str(c):
    c = conn.execute('SELECT * FROM patients').fetchall()
    print('Patients:', c)
conn.close()
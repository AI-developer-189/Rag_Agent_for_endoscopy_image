import sqlite3, os
db = r'F:\Multimodel\endoscopy.db'
print('Exists:', os.path.exists(db))
if os.path.exists(db):
    conn = sqlite3.connect(db)
    c = conn.execute('SELECT count(*) FROM patients')
    print('Patient count:', c.fetchone())
    c = conn.execute('PRAGMA table_info(patients)').fetchall()
    print('Columns:')
    for col in c:
        print('  ', col)
    c = conn.execute('SELECT * FROM patients').fetchall()
    print('Patients:', c)
    conn.close()
else:
    print('DB NOT FOUND')
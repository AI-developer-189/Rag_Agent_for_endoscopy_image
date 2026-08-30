import sqlite3
conn = sqlite3.connect(r'F:\Multimodel\endoscopy.db')
print('Before migration:')
c = conn.execute('PRAGMA table_info(patients)').fetchall()
for col in c:
    print(col)
conn.close()
import sqlite3
conn = sqlite3.connect(r'F:\Multimodel\endoscopy.db')
cursor = conn.execute('PRAGMA table_info(patients)')
columns = cursor.fetchall()
print('Columns:')
for c in columns:
    print(c)
conn.close()
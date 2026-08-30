import sqlite3
import os
db_path = r'F:\Multimodel\endoscopy.db'
print('File size before:', os.path.getsize(db_path) if os.path.exists(db_path) else 'NOT EXISTS')
conn = sqlite3.connect(db_path)
c = conn.execute('SELECT * FROM sqlite_master')
rows = c.fetchall()
print('Tables:', rows)
conn.close()
print('File size after:', os.path.getsize(db_path))
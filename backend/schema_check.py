import sqlite3
conn = sqlite3.connect('endoscopy.db')
c = conn.cursor()
c.execute('PRAGMA table_info(predictions)')
print('SQLite predictions table schema:')
for col in c.fetchall():
    print(f'  {col}')
conn.close()
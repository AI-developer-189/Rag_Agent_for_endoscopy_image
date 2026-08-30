import sqlite3
import os

db_path = 'endoscopy.db'
print(f"DB exists: {os.path.exists(db_path)}")
print(f"DB size: {os.path.getsize(db_path) if os.path.exists(db_path) else 0}")

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print("Tables:", tables)

for table_name in ['patients', 'users', 'predictions', 'studies']:
    c.execute(f'PRAGMA table_info({table_name})')
    print(f"{table_name} cols:", c.fetchall())
    
    c.execute(f'SELECT * FROM {table_name}')
    rows = c.fetchall()
    print(f"{table_name} rows:", len(rows))
    for r in rows[:3]:
        print(f"  {r}")

conn.close()
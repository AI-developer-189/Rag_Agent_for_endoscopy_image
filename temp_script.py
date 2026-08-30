from app.database import _migrate_schema, engine  
from sqlalchemy import inspector  
_migrate_schema()  
inspector = inspector(engine)  
existing_cols = {c['name'] for c in inspector.get_columns('patients')}  
print('Patients columns after migration:', sorted(existing_cols))  
if 'created_at' in existing_cols:  
    print('PASS: created_at column exists')  
else:  
    print('FAIL: created_at column is missing')  
if 'updated_at' in existing_cols:  
    print('PASS: updated_at column exists')  
else:  
    print('FAIL: updated_at column is missing') 

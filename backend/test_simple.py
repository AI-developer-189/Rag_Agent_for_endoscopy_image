from app.database import init_db, engine, _migrate_schema 
import requests  
"from sqlalchemy import inspect" 
""  
"print('=' * 60)"  
"print('FINAL VALIDATION TESTS')"  
"print('=' * 60)" 
""  
"_migrate_schema()"  
"insp = inspect(engine)"  
"existing_cols = {c['name'] for c in insp.get_columns('patients')}"  
"print(sorted(existing_cols))"  
"assert 'created_at' in existing_cols"  
"assert 'updated_at' in existing_cols"  

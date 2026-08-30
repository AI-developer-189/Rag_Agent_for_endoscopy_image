from fastapi.testclient import TestClient  
from app.main import app  
from app.database import init_db, engine, _migrate_schema  
from sqlalchemy import inspector  
import json  
import requests  
  
""  
print("=" * 60)  
print("FINAL VALIDATION TESTS")  
print("=" * 60) 

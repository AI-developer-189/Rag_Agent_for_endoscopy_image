"""
backend/app/models.py
Re-exports database models from database.py for backward compatibility.
"""
from app.database import (
    Base, User, Patient, Study, Prediction, ClinicalReport, Conversation, AuditLog
)

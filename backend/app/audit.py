"""
backend/app/audit.py
Helper functions and exports for audit logging.
"""
from app.database import AuditLog

def log_audit_event(db, action: str, details: str = None, user_id: int = None):
    """Log an event in the audit trail."""
    try:
        log = AuditLog(action=action, details=details, user_id=user_id)
        db.add(log)
        db.commit()
        return log
    except Exception as e:
        db.rollback()
        print(f"[Audit] Failed to log event: {e}")
        return None

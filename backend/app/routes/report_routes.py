"""
routes/report_routes.py
Report viewing and retrieval endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db, ClinicalReport, User
from app.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Reports"])


@router.get("/reports/{report_id}")
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full structured report JSON by report_id."""
    report = db.query(ClinicalReport).filter(ClinicalReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    if report.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return report.report_json
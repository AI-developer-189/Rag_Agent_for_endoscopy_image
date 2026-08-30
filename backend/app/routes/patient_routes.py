import os
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db, Patient, Prediction, Study, ClinicalReport, User
from app.auth import get_current_user

router = APIRouter(prefix="/api/patients", tags=["Patients"])


# ─── Schemas ──────────────────────────────────────────────────────────────────
class PatientCreate(BaseModel):
    full_name: str
    age: int
    sex: str
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    previous_endoscopy: Optional[str] = None
    family_history: Optional[str] = None


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    sex: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    previous_endoscopy: Optional[str] = None
    family_history: Optional[str] = None


class PatientResponse(BaseModel):
    id: str
    patient_ref: str
    full_name: str
    age: int
    sex: str
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    medications: Optional[str] = None
    previous_endoscopy: Optional[str] = None
    family_history: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


def _get_owned_patient(patient_id: str, db: Session, current_user: User) -> Patient:
    """Helper: fetch patient by id, enforce ownership, raise 404/403."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    if patient.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return patient


# ─── Routes ───────────────────────────────────────────────────────────────────
@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new patient record owned by the authenticated user."""
    patient_id = "PT-" + str(uuid.uuid4().int)[:4]
    while db.query(Patient).filter(Patient.id == patient_id).first():
        patient_id = "PT-" + str(uuid.uuid4().int)[:4]

    patient_ref = "PT-" + str(uuid.uuid4().int)[:6]

    patient = Patient(
        id=patient_id,
        patient_ref=patient_ref,
        user_id=current_user.id,
        full_name=payload.full_name.strip(),
        age=payload.age,
        sex=payload.sex,
        medical_history=payload.medical_history,
        allergies=payload.allergies,
        medications=payload.medications,
        previous_endoscopy=payload.previous_endoscopy,
        family_history=payload.family_history,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return PatientResponse.model_validate(patient)


@router.get("", response_model=List[PatientResponse])
def list_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all patients belonging to the authenticated user."""
    patients = (
        db.query(Patient)
        .filter(Patient.user_id == current_user.id)
        .order_by(Patient.created_at.desc())
        .all()
    )
    return [PatientResponse.model_validate(p) for p in patients]


@router.get("/{patient_ref}", response_model=PatientResponse)
def get_patient(
    patient_ref: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific patient — ownership enforced."""
    patient = db.query(Patient).filter(Patient.patient_ref == patient_ref).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    if patient.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return PatientResponse.model_validate(patient)


@router.get("/{patient_id}/predictions")
def get_patient_predictions(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get prediction history for a specific patient — ownership enforced."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found.")
    if patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    predictions = (
        db.query(Prediction)
        .filter(Prediction.patient_id == patient.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )

    return [
        {
            "id": p.id,
            "study_id": p.study_id,
            "predicted_disease": p.predicted_disease,
            "confidence": round(p.confidence * 100, 1),
            "low_confidence_warning": p.low_confidence_warning,
            "severity": p.severity_results or {},
            "heatmap_url": f"/static/outputs/{os.path.basename(p.heatmap_path)}" if p.heatmap_path else "",
            "created_at": p.created_at.isoformat(),
        }
        for p in predictions
    ]


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a patient record — ownership enforced."""
    patient = _get_owned_patient(patient_id, db, current_user)

    db.query(Prediction).filter(Prediction.patient_id == patient.id).delete()
    db.query(ClinicalReport).filter(
        ClinicalReport.study_id.in_(
            db.query(Study.id).filter(Study.patient_id == patient.id)
        )
    ).delete(synchronize_session=False)
    db.query(Study).filter(Study.patient_id == patient.id).delete()
    db.delete(patient)
    db.commit()
    return None


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: str,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a patient record — ownership enforced."""
    patient = _get_owned_patient(patient_id, db, current_user)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    patient.updated_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(patient)
    return PatientResponse.model_validate(patient)

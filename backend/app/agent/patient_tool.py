"""
agent/patient_tool.py
Retrieves patient history and previous predictions for the agentic orchestrator.
Enforces ownership — a user cannot access another user's patient data.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.database import Patient, Prediction, User


def get_patient_history(
    patient_id: int,
    current_user_id: int,
    db: Session,
) -> Dict[str, Any]:
    """
    Tool 2: Retrieve patient clinical history and previous predictions.

    Args:
        patient_id: Integer PK of the patient record
        current_user_id: ID of the authenticated user (for ownership check)
        db: SQLAlchemy session

    Returns:
        Patient info dict with previous predictions, or error dict if unauthorized/not found.
    """
    # Fetch patient with ownership check
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        return {
            "found": False,
            "error": "Patient not found.",
            "patient_id": patient_id,
        }

    if patient.user_id != current_user_id:
        return {
            "found": False,
            "error": "Access denied — this patient does not belong to your account.",
            "patient_id": patient_id,
        }

    # Fetch previous predictions for this patient
    previous_predictions = (
        db.query(Prediction)
        .filter(Prediction.patient_id == patient_id)
        .order_by(Prediction.created_at.desc())
        .limit(5)
        .all()
    )

    pred_history: List[Dict[str, Any]] = []
    for pred in previous_predictions:
        pred_history.append({
            "date": pred.created_at.isoformat(),
            "predicted_disease": pred.predicted_disease,
            "confidence": round(pred.confidence * 100, 1),
            "low_confidence_warning": pred.low_confidence_warning,
        })

    # Build risk context from patient fields
    risk_context: List[str] = []
    if patient.age and patient.age >= 60:
        risk_context.append(f"Age {patient.age}: elevated risk for adenoma and UC-associated dysplasia")
    if patient.medical_history and any(
        kw in patient.medical_history.lower()
        for kw in ["cancer", "malignancy", "carcinoma", "nsaid", "aspirin", "diabetes"]
    ):
        risk_context.append("Medical history includes relevant comorbidities — see full history")
    if patient.family_history and any(
        kw in patient.family_history.lower()
        for kw in ["cancer", "polyp", "colitis", "barrett"]
    ):
        risk_context.append("Family history includes GI malignancy or inflammatory bowel disease")
    if patient.medications and any(
        kw in patient.medications.lower()
        for kw in ["warfarin", "aspirin", "nsaid", "methotrexate", "azathioprine", "steroid"]
    ):
        risk_context.append("Current medications associated with increased GI risk")
    if previous_predictions:
        diseases = {p.predicted_disease for p in previous_predictions}
        if len(diseases) > 1 or any("ulcerative" in d or "polyp" in d for d in diseases):
            risk_context.append(f"Previous endoscopic findings: {', '.join(diseases)}")

    return {
        "found": True,
        "patient": {
            "id": patient.id,
            "patient_ref": patient.patient_ref,
            "full_name": patient.full_name,
            "age": patient.age,
            "sex": patient.sex,
            "medical_history": patient.medical_history or "Not recorded",
            "allergies": patient.allergies or "None recorded",
            "medications": patient.medications or "None recorded",
            "previous_endoscopy": patient.previous_endoscopy or "None recorded",
            "family_history": patient.family_history or "None recorded",
        },
        "risk_context": risk_context,
        "previous_predictions": pred_history,
    }

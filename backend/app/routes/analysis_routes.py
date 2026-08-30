"""
routes/analysis_routes.py
Core unified analysis endpoint: POST /api/analyze
Full workflow: authenticate → validate patient → Swin → Grad-CAM → Agent → save → return
"""
import os
import uuid
import shutil
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
import datetime

from app.database import get_db, Patient, Study, Prediction, ClinicalReport, AuditLog, User
from app.auth import get_current_user
from app.agent.agent import clinical_agent
from app.pipeline import preprocess_image, segment_image, quantify_severity

router = APIRouter(prefix="/api", tags=["Analysis"])

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def _validate_image_file(file: UploadFile) -> None:
    """Validate file type and extension."""
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: JPEG, PNG, WEBP, BMP. Got: {ext or 'unknown'}",
        )
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a valid endoscopy image.",
        )


@router.post("/analyze")
async def analyze(
    image: UploadFile = File(..., description="Endoscopy image file"),
    patient_ref: str = Form(..., description="Patient reference (e.g. PT-3032)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    POST /api/analyze
    Full clinical analysis pipeline:
    1. Authenticate user
    2. Validate patient ownership
    3. Save uploaded image
    4. Run Swin Transformer prediction + Grad-CAM
    5. Run agentic analysis (Patient Tool + RAG Tool + LLM reasoning)
    6. Save prediction + report to database
    7. Return structured response
    """
    # ── Validate image file ──────────────────────────────────────────────────
    _validate_image_file(image)

    # Read file content and check size
    image_content = await image.read()
    if len(image_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file too large. Maximum allowed size is 20MB.",
        )

    # ── Verify patient ownership ─────────────────────────────────────────────
    patient = db.query(Patient).filter(Patient.patient_ref == patient_ref).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    if patient.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    # ── Save image file ──────────────────────────────────────────────────────
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ext = os.path.splitext(image.filename or "image.jpg")[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    image_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(image_path, "wb") as f:
        f.write(image_content)

    # ── Register study in DB ─────────────────────────────────────────────────
    study_id = "ST-" + str(uuid.uuid4().int)[:8]
    study = Study(
        id=study_id,
        patient_id=patient.id,
        original_image_path=image_path,
    )
    db.add(study)
    db.commit()
    db.refresh(study)

    try:
        # ── Stage 1: Image preprocessing ────────────────────────────────────
        prep = preprocess_image(image_path, OUTPUT_DIR)

        # ── Stage 2-3: Agent (Swin + Patient + RAG + LLM) ───────────────────
        agent_response = clinical_agent.run(
            image_path=image_path,
            patient_id=patient.id,  # String ID like "PT-1234"
            current_user_id=current_user.id,
            db=db,
            output_dir=OUTPUT_DIR,
        )

        raw_pred = agent_response.pop("_prediction", {})
        patient_summary = agent_response.pop("_patient", {})

        # ── Stage 4: Segmentation + severity ────────────────────────────────
        # Use predicted disease label for segmentation
        disease_label = raw_pred.get("predicted_disease", "unknown")
        # Map new class names to legacy segmentation labels
        seg_label_map = {
            "dyed-lifted-polyps": "Colon Polyp",
            "dyed-resection-margins": "Colon Polyp",
            "esophagitis": "Esophagitis",
            "normal-cecum": "Normal Mucosa",
            "normal-pylorus": "Normal Mucosa",
            "normal-z-line": "Normal Mucosa",
            "polyps": "Colon Polyp",
            "ulcerative-colitis": "Esophagitis",
        }
        seg_disease = seg_label_map.get(disease_label, "Normal Mucosa")

        seg_results = {"contours": [], "mask_path": "", "overlay_path": "", "confidence_map_path": ""}
        sev_results = {"percent_coverage": 0.0, "severity_level": "Normal"}

        try:
            # Rough hotspot center from center of image for segmentation
            import cv2
            img_cv = cv2.imread(image_path)
            if img_cv is not None:
                h, w = img_cv.shape[:2]
                seg_results = segment_image(
                    prep["preprocessed_path"],
                    seg_disease,
                    (w // 2, h // 2),
                    OUTPUT_DIR,
                )
                sev_results = quantify_severity(
                    prep["preprocessed_path"],
                    seg_results["mask_path"],
                    seg_disease,
                )
        except Exception as seg_err:
            print(f"[Analyze] Segmentation failed (non-critical): {seg_err}")

        # ── Save prediction to DB ────────────────────────────────────────────
        existing_pred = db.query(Prediction).filter(Prediction.study_id == study_id).first()
        if existing_pred:
            db.delete(existing_pred)

        prediction_db = Prediction(
            study_id=study_id,
            patient_id=patient.id,
            user_id=current_user.id,
            predicted_disease=raw_pred.get("predicted_disease", "unknown"),
            confidence=raw_pred.get("confidence", 0.0),
            low_confidence_warning=raw_pred.get("low_confidence_warning", False),
            classification_probs=raw_pred.get("class_probabilities", {}),
            classification_results=raw_pred.get("class_probabilities", {}),
            preprocessed_path=prep.get("preprocessed_path", ""),
            heatmap_path=raw_pred.get("heatmap_path", ""),
            blur_score=prep.get("blur_score", 0),
            segmentation_results={
                "mask_path": seg_results.get("mask_path", ""),
                "overlay_path": seg_results.get("overlay_path", ""),
                "contours": seg_results.get("contours", []),
            },
            severity_results=sev_results,
            agent_analysis=agent_response,
        )
        db.add(prediction_db)

        # ── Save clinical report ─────────────────────────────────────────────
        report_id = "RP-" + str(uuid.uuid4().int)[:8]
        report_data = {
            "report_id": report_id,
            "study_id": study_id,
            "patient": patient_summary,
            "prediction": raw_pred,
            "severity": sev_results,
            "agent_analysis": agent_response,
            "generated_at": datetime.datetime.utcnow().isoformat(),
        }

        existing_report = db.query(ClinicalReport).filter(ClinicalReport.study_id == study_id).first()
        if existing_report:
            db.delete(existing_report)

        clinical_report = ClinicalReport(
            id=report_id,
            study_id=study_id,
            user_id=current_user.id,
            report_json=report_data,
            pdf_path="",
        )
        db.add(clinical_report)

        # ── Audit log ────────────────────────────────────────────────────────
        log = AuditLog(
            action="ANALYZE",
            details=f"Analysis for patient {patient.patient_ref}: {raw_pred.get('predicted_disease')} ({round(raw_pred.get('confidence', 0)*100, 1)}%)",
            user_id=current_user.id,
        )
        db.add(log)
        db.commit()

        # ── Format image URLs for response ───────────────────────────────────
        image_urls = {
            "original": f"/static/uploads/{os.path.basename(image_path)}",
            "preprocessed": f"/static/outputs/{os.path.basename(prep.get('preprocessed_path', ''))}" if prep.get("preprocessed_path") else "",
            "heatmap": f"/static/outputs/{os.path.basename(raw_pred.get('heatmap_path', ''))}" if raw_pred.get("heatmap_path") else "",
            "overlay": f"/static/outputs/{os.path.basename(seg_results.get('overlay_path', ''))}" if seg_results.get("overlay_path") else "",
        }

        return {
            "status": "success",
            "study_id": study_id,
            "report_id": report_id,
            "patient": {
                "id": patient.id,
                "patient_ref": patient.patient_ref,
                "full_name": patient.full_name,
                "age": patient.age,
                "sex": patient.sex,
            },
            "prediction": {
                "predicted_disease": raw_pred.get("predicted_disease"),
                "confidence": raw_pred.get("confidence"),
                "confidence_percentage": raw_pred.get("confidence_percentage"),
                "confidence_threshold": raw_pred.get("confidence_threshold", 85.0),
                "low_confidence_warning": raw_pred.get("low_confidence_warning"),
                "warning_message": raw_pred.get("warning_message", ""),
                "class_probabilities": raw_pred.get("class_probabilities", {}),
                "model_used": raw_pred.get("model_used", "unknown"),
            },
            "gradcam": {
                "heatmap_base64": raw_pred.get("heatmap_base64", ""),
                "heatmap_url": image_urls["heatmap"],
            },
            "image_urls": image_urls,
            "blur_score": prep.get("blur_score", 0),
            "severity": sev_results,
            "segmentation": {
                "contours": seg_results.get("contours", []),
                "overlay_url": image_urls["overlay"],
            },
            "agent_analysis": agent_response,
        }

    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process the image. Please try again.",
        )


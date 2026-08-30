import os
import shutil
from app.database import init_db, SessionLocal, Patient, Study, Prediction, ClinicalReport, AuditLog
from app.pipeline import preprocess_image, classify_image, segment_image, quantify_severity, search_similar_cases
from app.orchestrator import run_orchestrator
from app.pdf_gen import generate_report_pdf

def test_pipeline():
    print("Initializing test database...")
    init_db()
    db = SessionLocal()

    # Verify Patient exists
    patient = db.query(Patient).filter(Patient.id == "PT-3841").first()
    if not patient:
        patient = Patient(id="PT-3841", name="Sarah Jenkins", age=45, gender="Female")
        db.add(patient)
        db.commit()
        db.refresh(patient)

    print(f"Patient found: {patient.name} ({patient.id})")

    # Target test image from samples folder
    sample_img = "f:/Multimodel/samples/gastric_ulcer.png"
    if not os.path.exists(sample_img):
        raise FileNotFoundError(f"Test image not found at {sample_img}")

    # Set up test folders
    uploads_dir = "uploads"
    outputs_dir = "outputs"
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    # Copy image to uploads to simulate upload stage
    dest_path = os.path.join(uploads_dir, "test_ulcer.png")
    shutil.copyfile(sample_img, dest_path)
    print(f"Sample copied to upload folder: {dest_path}")

    # Register Study
    study_id = "ST-TEST-01"
    existing_study = db.query(Study).filter(Study.id == study_id).first()
    if existing_study:
        db.delete(existing_study)
        db.commit()

    study = Study(id=study_id, patient_id=patient.id, original_image_path=dest_path)
    db.add(study)
    db.commit()
    db.refresh(study)
    print(f"Registered Study: {study.id}")

    # Stage 1: Preprocessing
    print("\n--- Executing Stage 1: Vision Preprocessing ---")
    prep = preprocess_image(study.original_image_path, outputs_dir)
    print(f"Enhanced Image Path: {prep['preprocessed_path']}")
    print(f"Blur Assessment Score: {prep['blur_score']}")

    # Stage 2: Disease Classification
    print("\n--- Executing Stage 2: Classification ---")
    cls = classify_image(prep["preprocessed_path"], os.path.basename(study.original_image_path), outputs_dir)
    print(f"Predicted Diagnosis: {cls['label']}")
    print(f"Classification Confidence: {cls['confidence']}")
    print(f"Grad-CAM Heatmap Path: {cls['heatmap_path']}")

    # Stage 3: Lesion Segmentation
    print("\n--- Executing Stage 3: Segmentation ---")
    seg = segment_image(prep["preprocessed_path"], cls["label"], cls["hotspot_center"], outputs_dir)
    print(f"Lesion Contours Count: {len(seg['contours'])}")
    print(f"Confidence Map Path: {seg['confidence_map_path']}")

    # Stage 4: Affected Area & Severity Quantification
    print("\n--- Executing Stage 4: Quantification ---")
    sev = quantify_severity(prep["preprocessed_path"], seg["mask_path"], cls["label"])
    print(f"Lesion Affected Area Coverage: {sev['percent_coverage']}%")
    print(f"Severity Bucket: {sev['severity_level']}")

    # Stage 5: Similarity retrieval
    print("\n--- Executing Stage 5: Similarity Index Search ---")
    sim = search_similar_cases(cls["label"], sev["severity_level"], cls["embedding"])
    print(f"Nearest-neighbor Matches Found: {len(sim)}")
    for match in sim:
        print(f" - Case {match['case_id']} ({match['diagnosis']}): {match['similarity_score']}% match")

    # Stage 6: LangGraph Clinical Report Orchestration
    print("\n--- Executing Stage 6: LangGraph Report Generation & Safety Node ---")
    pipeline_data = {
        "patient_id": patient.id,
        "patient_name": patient.name,
        "patient_age": patient.age,
        "patient_gender": patient.gender,
        "original_image_path": study.original_image_path,
        "preprocessed_path": prep["preprocessed_path"],
        "blur_score": prep["blur_score"],
        "classification": cls,
        "segmentation": seg,
        "severity": sev
    }

    orchestration_state = run_orchestrator(pipeline_data)
    report = orchestration_state["validated_report"]
    warnings = orchestration_state["warnings"]
    print("Orchestrated Structured Report JSON:")
    import pprint
    pprint.pprint(report)
    print(f"Warnings Triggered: {warnings}")

    # Generate Report PDF
    pdf_path = os.path.join(outputs_dir, "pdfs", f"test_report_{study_id}.pdf")
    print(f"\nCompiling PDF report to {pdf_path}...")
    generate_report_pdf(
        report_data=report,
        original_img=study.original_image_path,
        preprocessed_img=prep["preprocessed_path"],
        heatmap_img=cls["heatmap_path"],
        overlay_img=seg["overlay_path"],
        output_pdf_path=pdf_path
    )
    print("PDF compilation successful.")

    # Clean up DB
    db.close()
    print("\nTest pipeline passed successfully!")

if __name__ == "__main__":
    test_pipeline()

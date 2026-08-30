import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db, AuditLog, SessionLocal
from app.routes.auth_routes import router as auth_router
from app.routes.patient_routes import router as patient_router
from app.routes.analysis_routes import router as analysis_router
from app.routes.report_routes import router as report_router
from app.model.model_loader import load_model
from app.rag.embeddings import build_index

app = FastAPI(
    title="AI Endoscopy Clinical Decision Support System API",
    description="Agentic AI-based Endoscopy CDSS using Swin Transformer, Grad-CAM, RAG and Clinical Practice Guidelines",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads and outputs
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
for d in [UPLOAD_DIR, OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)

app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/static/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# Include Routers
app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(analysis_router)
app.include_router(report_router)


@app.on_event("startup")
def startup_event():
    print("[Startup] Initializing Database...")
    init_db()

    print("[Startup] Loading Swin Transformer model...")
    load_model()

    print("[Startup] Building RAG embedding index...")
    build_index()

    db = SessionLocal()
    try:
        log = AuditLog(action="STARTUP", details="FastAPI server started with all components initialized.")
        db.add(log)
        db.commit()
    except Exception as e:
        print(f"[Startup] Audit log failed: {e}")
    finally:
        db.close()

    print("🚀 Endoscopy CDSS Backend Ready.")


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "AI Endoscopy Clinical Decision Support System",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
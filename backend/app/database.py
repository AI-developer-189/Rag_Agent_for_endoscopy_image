import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean, Float, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///./endoscopy.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """Registered clinician / researcher account."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patients = relationship("Patient", back_populates="owner")
    conversations = relationship("Conversation", back_populates="user")


class Patient(Base):
    """Patient profile owned by a specific user account."""
    __tablename__ = "patients"

    id = Column(String, primary_key=True)
    patient_ref = Column(String, unique=True, index=True)  # Human-readable e.g. PT-3841
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String, nullable=False)
    medical_history = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    medications = Column(Text, nullable=True)
    previous_endoscopy = Column(Text, nullable=True)
    family_history = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    owner = relationship("User", back_populates="patients")
    studies = relationship("Study", back_populates="patient")
    predictions = relationship("Prediction", back_populates="patient")


class Study(Base):
    """An endoscopy imaging session linked to a patient."""
    __tablename__ = "studies"

    id = Column(String, primary_key=True, index=True)  # e.g., ST-89301
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    original_image_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="studies")
    predictions = relationship("Prediction", back_populates="study", uselist=False)
    reports = relationship("ClinicalReport", back_populates="study", uselist=False)


class Prediction(Base):
    """Stores Swin Transformer prediction + Grad-CAM + agent analysis for one study."""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    study_id = Column(String, ForeignKey("studies.id"), unique=True, nullable=False)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Swin classification results
    predicted_disease = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    low_confidence_warning = Column(Boolean, default=False)
    classification_probs = Column(JSON, nullable=True)  # {class: prob, ...}
    classification_results = Column(JSON, nullable=False)  # Complete classification result

    # Image paths
    preprocessed_path = Column(String, nullable=True)
    heatmap_path = Column(String, nullable=True)
    blur_score = Column(Integer, nullable=True)

    # Segmentation / severity
    segmentation_results = Column(JSON, nullable=True)
    severity_results = Column(JSON, nullable=True)

    # Agent analysis (structured JSON)
    agent_analysis = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    study = relationship("Study", back_populates="predictions")
    patient = relationship("Patient", back_populates="predictions")


class ClinicalReport(Base):
    """Full structured report for a study."""
    __tablename__ = "clinical_reports"

    id = Column(String, primary_key=True, index=True)  # e.g., RP-48201
    study_id = Column(String, ForeignKey("studies.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    report_json = Column(JSON, nullable=False)
    pdf_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    study = relationship("Study", back_populates="reports")


class Conversation(Base):
    """Agent conversation history per user."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    study_id = Column(String, nullable=True)
    messages = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="conversations")


class AuditLog(Base):
    """System-level audit trail."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    user_id = Column(Integer, nullable=True)  # Nullable for system actions


def _migrate_schema():
    """
    Idempotent schema migration for existing SQLite databases.
    Adds any missing columns to pre-existing tables without dropping data.
    Also migrates legacy 'name' column data to 'full_name' and removes 'name'.
    """
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        migrations = {
            "audit_logs": [
                ("user_id", "INTEGER"),
            ],
            "patients": [
                ("user_id", "INTEGER"),
                ("patient_ref", "VARCHAR"),
                ("full_name", "VARCHAR"),
                ("sex", "VARCHAR"),
                ("medical_history", "TEXT"),
                ("allergies", "TEXT"),
                ("medications", "TEXT"),
                ("previous_endoscopy", "TEXT"),
                ("family_history", "TEXT"),
                ("created_at", "DATETIME"),
                ("updated_at", "DATETIME"),
            ],
            "predictions": [
                ("patient_id", "INTEGER"),
                ("user_id", "INTEGER"),
                ("predicted_disease", "VARCHAR"),
                ("confidence", "FLOAT"),
                ("low_confidence_warning", "BOOLEAN"),
                ("classification_probs", "JSON"),
                ("classification_results", "JSON"),
                ("agent_analysis", "JSON"),
                ("preprocessed_path", "VARCHAR"),
                ("heatmap_path", "VARCHAR"),
                ("blur_score", "INTEGER"),
                ("segmentation_results", "JSON"),
                ("severity_results", "JSON"),
            ],
            "clinical_reports": [
                ("user_id", "INTEGER"),
            ],
        }

        with engine.connect() as conn:
            for table_name, columns in migrations.items():
                if table_name in existing_tables:
                    existing_cols = {c["name"] for c in inspector.get_columns(table_name)}
                    for col_name, col_type in columns:
                        if col_name not in existing_cols:
                            print(f"[DB Migration] Adding missing column '{col_name}' ({col_type}) to table '{table_name}'...")
                            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};"))
                    # Populate created_at for existing rows that have NULL
                    if table_name == "patients":
                        conn.execute(
                            text(
                                "UPDATE patients SET created_at = datetime('now') WHERE created_at IS NULL;"
                            )
                        )
                        # Populate updated_at for existing rows that have NULL
                        conn.execute(
                            text(
                                "UPDATE patients SET updated_at = datetime('now') WHERE updated_at IS NULL;"
                            )
                        )

# Migrate legacy 'name' column to 'full_name' if needed
            existing_patient_cols = {c["name"] for c in inspector.get_columns("patients")}
            if "patients" in existing_tables and "name" in existing_patient_cols and "full_name" in existing_patient_cols:
                # Copy data from legacy 'name' to 'full_name' where full_name is NULL
                conn.execute(
                    text(
                        "UPDATE patients SET full_name = name WHERE full_name IS NULL;"
                    )
                )
                # Copy data from legacy 'gender' to 'sex' where sex is NULL
                conn.execute(
                    text(
                        "UPDATE patients SET sex = gender WHERE sex IS NULL;"
                    )
                )
                # Remove the NOT NULL constraint on name by recreating the table
                conn.execute(text("CREATE TABLE patients_new ("
                    "id TEXT PRIMARY KEY, "
                    "patient_ref TEXT UNIQUE, "
                    "user_id INTEGER, "
                    "full_name TEXT NOT NULL, "
                    "age INTEGER NOT NULL, "
                    "sex TEXT NOT NULL, "
                    "medical_history TEXT, "
                    "allergies TEXT, "
                    "medications TEXT, "
                    "previous_endoscopy TEXT, "
                    "family_history TEXT, "
                    "created_at DATETIME, "
                    "updated_at DATETIME"
                    ");"))
                conn.execute(text(
                    "INSERT INTO patients_new SELECT id, patient_ref, user_id, full_name, age, sex, "
                    "medical_history, allergies, medications, previous_endoscopy, family_history, "
                    "created_at, updated_at FROM patients;"
                ))
                conn.execute(text("DROP TABLE patients;"))
                conn.execute(text("ALTER TABLE patients_new RENAME TO patients;"))
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_patients_patient_ref ON patients(patient_ref);"))
            conn.commit()
    except Exception as e:
        print(f"[DB Migration] ⚠️ Schema migration warning: {e}")


def init_db():
    Base.metadata.create_all(bind=engine)
    _migrate_schema()
    print("✅ Database tables initialized and schema migration verified.")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

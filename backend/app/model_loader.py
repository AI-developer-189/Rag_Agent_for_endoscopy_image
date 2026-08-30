"""
backend/app/model_loader.py
Re-exports model_loader functionality for convenience.
"""
from app.model.model_loader import (
    load_model, get_model, get_image_processor, get_feature_extractor,
    get_disease_classes, is_model_loaded, CONFIDENCE_THRESHOLD
)

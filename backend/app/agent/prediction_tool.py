"""
agent/prediction_tool.py
Wraps model_utils.build_prediction_response() for use by the agentic orchestrator.
Does NOT reload the model — uses the singleton loaded at startup.
"""
from typing import Dict, Any

from app.model.model_utils import build_prediction_response
from app.model.model_loader import CONFIDENCE_THRESHOLD


def run_prediction_tool(image_path: str, output_dir: str = "outputs") -> Dict[str, Any]:
    """
    Tool 1: Run Swin Transformer inference + Grad-CAM on an uploaded image.

    Returns:
        {
            predicted_disease: str,
            confidence: float,
            confidence_percentage: float,
            confidence_threshold: float,
            low_confidence_warning: bool,
            warning_message: str,
            class_probabilities: dict,
            heatmap_path: str,
            heatmap_base64: str,
            model_used: str,
        }
    """
    try:
        result = build_prediction_response(image_path, output_dir)
        return result
    except Exception as e:
        return {
            "predicted_disease": "unknown",
            "confidence": 0.0,
            "confidence_percentage": 0.0,
            "confidence_threshold": CONFIDENCE_THRESHOLD * 100,
            "low_confidence_warning": True,
            "warning_message": f"Prediction tool encountered an error: {str(e)}",
            "class_probabilities": {},
            "heatmap_path": "",
            "heatmap_base64": "",
            "model_used": "error",
        }

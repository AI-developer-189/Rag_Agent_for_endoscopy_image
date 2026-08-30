"""
model/model_loader.py
Loads the public Kvasir-v2 vision classifier model from Hugging Face:
mmuratarat/kvasir-v2-classifier
"""
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from transformers import AutoImageProcessor, AutoModelForImageClassification
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

MODEL_NAME = "mmuratarat/kvasir-v2-classifier"
CONFIDENCE_THRESHOLD = 0.85  # 85%

# ─── Disease classes (one source of truth) ────────────────────────────────────
DISEASE_CLASSES = [
    "dyed-lifted-polyps",
    "dyed-resection-margins",
    "esophagitis",
    "normal-cecum",
    "normal-pylorus",
    "normal-z-line",
    "polyps",
    "ulcerative-colitis",
]

# ─── Singleton model state ────────────────────────────────────────────────────
_model = None
_image_processor = None
_model_loaded = False
_disease_classes = []


def load_model():
    """Load mmuratarat/kvasir-v2-classifier from Hugging Face."""
    global _model, _image_processor, _model_loaded, _disease_classes

    try:
        print(f"[ModelLoader] Loading image processor from '{MODEL_NAME}'...")
        _image_processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

        print(f"[ModelLoader] Loading classification model from '{MODEL_NAME}'...")
        _model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)
        _model.eval()

        # Read class labels from model config
        if hasattr(_model.config, "id2label") and _model.config.id2label:
            _disease_classes = [
                _model.config.id2label[i] for i in range(len(_model.config.id2label))
            ]
        else:
            _disease_classes = [
                "dyed-lifted-polyps",
                "dyed-resection-margins",
                "esophagitis",
                "normal-cecum",
                "normal-pylorus",
                "normal-z-line",
                "polyps",
                "ulcerative-colitis",
            ]

        _model_loaded = True
        print(f"[ModelLoader] ✅ Vision model loaded successfully. Classes ({len(_disease_classes)}): {_disease_classes}")

    except Exception as e:
        _model_loaded = False
        print(f"[ModelLoader] ❌ Failed to load vision model '{MODEL_NAME}': {e}")
        raise RuntimeError(
            f"Failed to load vision classifier '{MODEL_NAME}': {e}"
        ) from e


def get_model():
    """Return the loaded vision model instance."""
    if not _model_loaded or _model is None:
        raise RuntimeError("Vision model is not loaded.")
    return _model


def get_image_processor():
    """Return the loaded image processor instance."""
    if not _model_loaded or _image_processor is None:
        raise RuntimeError("Image processor is not loaded.")
    return _image_processor


def get_feature_extractor():
    """Alias for backwards compatibility with get_image_processor."""
    return get_image_processor()


def get_disease_classes():
    """Return list of disease class names."""
    return _disease_classes


def is_model_loaded() -> bool:
    return _model_loaded

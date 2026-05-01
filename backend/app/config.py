"""FastAPI app configuration / paths."""
from __future__ import annotations

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
SAVED_MODELS_DIR = BACKEND_DIR / "saved_models"

CLASS_NAMES = ["Benign", "Malignant"]  # alphabetical → matches training
IMG_SIZE = (224, 224)

# Each entry: backend key, display name, file under saved_models/.
MODEL_REGISTRY = [
    {"key": "cnn",    "display": "Simple CNN",       "filename": "cnn.keras"},
    {"key": "resnet", "display": "ResNet (ResNet50)", "filename": "resnet.keras"},
    {"key": "mlp",    "display": "MLP",              "filename": "mlp.keras"},
]

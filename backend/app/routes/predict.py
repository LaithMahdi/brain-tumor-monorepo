"""Inference + introspection endpoints."""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..config import MODEL_REGISTRY
from ..services.inference import store
from ..utils.image_processing import bytes_to_input_tensor

router = APIRouter(prefix="/api", tags=["inference"])


@router.get("/health")
def health():
    return {"status": "ok", "models_loaded": store.loaded_keys()}


@router.get("/models")
def list_models():
    payload = []
    for entry in MODEL_REGISTRY:
        payload.append(
            {
                "key": entry["key"],
                "display_name": entry["display"],
                "available": store.is_loaded(entry["key"]),
                "metrics": store.metadata.get(entry["key"]),
            }
        )
    return {"models": payload}


@router.post("/predict")
async def predict(image: UploadFile = File(...)):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content type: {image.content_type}. Please upload an image.",
        )

    raw = await image.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file.")

    try:
        x = bytes_to_input_tensor(raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    predictions = store.predict_all(x)
    if not any(p["available"] for p in predictions):
        raise HTTPException(
            status_code=503,
            detail=(
                "No trained models are available. "
                "Train at least one model first (see backend/training/)."
            ),
        )

    return {
        "filename": image.filename,
        "predictions": predictions,
    }

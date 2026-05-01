"""Loads the saved Keras models once and exposes a single predict() entrypoint."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from ..config import CLASS_NAMES, MODEL_REGISTRY, SAVED_MODELS_DIR

logger = logging.getLogger(__name__)


class ModelStore:
    """Holds every successfully-loaded Keras model + its saved metadata."""

    def __init__(self) -> None:
        self.models: dict[str, Any] = {}
        self.metadata: dict[str, dict] = {}

    def load_all(self) -> None:
        # Only import TensorFlow if there are actual model files to load.
        # This prevents a multi-minute TF initialisation freeze when no models
        # have been trained yet and lets the API start up immediately.
        models_to_load = [
            entry for entry in MODEL_REGISTRY
            if (SAVED_MODELS_DIR / entry["filename"]).exists()
        ]

        if not models_to_load:
            logger.warning(
                "No saved model files found in %s — skipping TensorFlow import. "
                "Train the models first (see backend/training/).",
                SAVED_MODELS_DIR,
            )
            return

        # Lazy-import TensorFlow only when we have files to load.
        from tensorflow.keras.models import load_model  # noqa: PLC0415

        for entry in models_to_load:
            path = SAVED_MODELS_DIR / entry["filename"]
            meta_path = path.with_suffix(".json")
            try:
                self.models[entry["key"]] = load_model(path)
                logger.info("Loaded model %s from %s", entry["key"], path)
            except Exception:
                logger.exception("Failed to load model %s", entry["key"])
                continue

            if meta_path.exists():
                try:
                    self.metadata[entry["key"]] = json.loads(meta_path.read_text())
                except Exception:
                    logger.exception("Failed to read metadata %s", meta_path)

    def is_loaded(self, key: str) -> bool:
        return key in self.models

    def loaded_keys(self) -> list[str]:
        return list(self.models.keys())

    def predict_all(self, x: np.ndarray) -> list[dict]:
        """Run inference on every loaded model. `x` shape: (1, 224, 224, 3) float32."""
        results: list[dict] = []
        for entry in MODEL_REGISTRY:
            key = entry["key"]
            if key not in self.models:
                results.append(
                    {
                        "model": key,
                        "display_name": entry["display"],
                        "available": False,
                        "error": "Model not loaded — train it first.",
                    }
                )
                continue

            try:
                prob = float(self.models[key].predict(x, verbose=0).flatten()[0])
            except Exception as exc:
                logger.exception("Inference failed for %s", key)
                results.append(
                    {
                        "model": key,
                        "display_name": entry["display"],
                        "available": False,
                        "error": str(exc),
                    }
                )
                continue

            label_idx = 1 if prob > 0.5 else 0
            label = CLASS_NAMES[label_idx]
            confidence = prob if label_idx == 1 else 1.0 - prob

            results.append(
                {
                    "model": key,
                    "display_name": entry["display"],
                    "available": True,
                    "probability_malignant": prob,
                    "label": label,
                    "confidence": confidence,
                    "metrics": self.metadata.get(key),
                }
            )
        return results


# Singleton — populated in app.main on startup.
store = ModelStore()

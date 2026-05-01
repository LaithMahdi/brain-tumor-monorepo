"""Decode raw upload bytes → 224×224×3 float32 tensor batch."""
from __future__ import annotations

import io

import numpy as np
from PIL import Image

from ..config import IMG_SIZE


def bytes_to_input_tensor(raw: bytes) -> np.ndarray:
    """Convert uploaded image bytes to a (1, 224, 224, 3) float32 array.

    The trained models include `Rescaling(1./255)` as their first layer (CNN/MLP)
    or use `tf.keras.applications.ResNet50` which is robust to raw 0–255 inputs;
    so we keep pixels in [0, 255] here.
    """
    try:
        img = Image.open(io.BytesIO(raw))
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"Could not decode image: {exc}") from exc

    img = img.convert("RGB").resize(IMG_SIZE)
    arr = np.asarray(img, dtype=np.float32)  # (H, W, 3) in [0, 255]
    return arr[np.newaxis, ...]  # (1, H, W, 3)

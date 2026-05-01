"""Train the simple CNN model. Mirrors the notebook architecture exactly.

Run from `backend/`:
    python -m training.train_cnn
"""
from __future__ import annotations

import tensorflow as tf
from tensorflow.keras import layers, models

from .config import EPOCHS, SAVED_MODELS_DIR
from .data_loader import load_datasets, metric_set
from ._save_metrics import evaluate_and_save


def build_cnn() -> tf.keras.Model:
    return models.Sequential(
        [
            layers.Input(shape=(224, 224, 3)),
            layers.Rescaling(1.0 / 255),
            layers.Conv2D(16, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(32, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, activation="relu"),
            layers.MaxPooling2D(),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ],
        name="cnn",
    )


def main():
    train_ds, val_ds, test_ds = load_datasets()

    model = build_cnn()
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=metric_set(),
    )
    model.summary()

    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

    out_path = SAVED_MODELS_DIR / "cnn.keras"
    model.save(out_path)
    print(f"Saved CNN -> {out_path}")

    evaluate_and_save(model, test_ds, "cnn", out_path)


if __name__ == "__main__":
    main()

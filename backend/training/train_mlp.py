"""Train the MLP baseline (flatten + dense layers + dropout). Matches the notebook.

Run from `backend/`:
    python -m training.train_mlp
"""
from __future__ import annotations

import tensorflow as tf
from tensorflow.keras import layers, models

from .config import EPOCHS, SAVED_MODELS_DIR
from .data_loader import load_datasets, metric_set
from ._save_metrics import evaluate_and_save


def build_mlp() -> tf.keras.Model:
    return models.Sequential(
        [
            layers.Input(shape=(224, 224, 3)),
            layers.Rescaling(1.0 / 255),
            layers.Flatten(),
            layers.Dense(512, activation="relu"),
            layers.Dropout(0.3),
            layers.Dense(256, activation="relu"),
            layers.Dropout(0.3),
            layers.Dense(1, activation="sigmoid"),
        ],
        name="mlp",
    )


def main():
    train_ds, val_ds, test_ds = load_datasets()

    model = build_mlp()
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=metric_set(),
    )
    model.summary()

    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

    out_path = SAVED_MODELS_DIR / "mlp.keras"
    model.save(out_path)
    print(f"Saved MLP -> {out_path}")

    evaluate_and_save(model, test_ds, "mlp", out_path)


if __name__ == "__main__":
    main()

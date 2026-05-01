"""Train the ResNet50 transfer-learning model (frozen ImageNet base + small head).

The notebook's "ResNet18" section actually uses ResNet50 — `tf.keras.applications`
ships ResNet50 but not ResNet18 — so we keep ResNet50 here.

Run from `backend/`:
    python -m training.train_resnet
"""
from __future__ import annotations

import tensorflow as tf
from tensorflow.keras import layers, models

from .config import EPOCHS, SAVED_MODELS_DIR
from .data_loader import load_datasets, metric_set
from ._save_metrics import evaluate_and_save


def build_resnet() -> tf.keras.Model:
    base_model = tf.keras.applications.ResNet50(
        include_top=False,
        input_shape=(224, 224, 3),
        weights="imagenet",
    )
    base_model.trainable = False

    return models.Sequential(
        [
            layers.Input(shape=(224, 224, 3)),
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(128, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ],
        name="resnet",
    )


def main():
    train_ds, val_ds, test_ds = load_datasets()

    model = build_resnet()
    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=metric_set(),
    )
    model.summary()

    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS)

    out_path = SAVED_MODELS_DIR / "resnet.keras"
    model.save(out_path)
    print(f"Saved ResNet -> {out_path}")

    evaluate_and_save(model, test_ds, "resnet", out_path)


if __name__ == "__main__":
    main()

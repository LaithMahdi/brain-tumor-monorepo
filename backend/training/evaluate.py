"""Evaluate every trained model on the test set and print the classification report.

Run from `backend/`:
    python -m training.evaluate
"""
from __future__ import annotations

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, roc_auc_score

from .config import SAVED_MODELS_DIR
from .data_loader import load_datasets

MODEL_FILES = {
    "CNN": SAVED_MODELS_DIR / "cnn.keras",
    "ResNet": SAVED_MODELS_DIR / "resnet.keras",
    "MLP": SAVED_MODELS_DIR / "mlp.keras",
}


def evaluate_model(model: tf.keras.Model, dataset) -> None:
    y_true, y_prob = [], []
    for images, labels in dataset:
        preds = model.predict(images, verbose=0).flatten()
        y_true.extend(labels.numpy().tolist())
        y_prob.extend(preds.tolist())

    y_true = np.array(y_true)
    y_prob = np.array(y_prob)
    y_pred = (y_prob > 0.5).astype(int)

    print("Classification report:\n")
    print(classification_report(y_true, y_pred, target_names=["Benign", "Malignant"], zero_division=0))
    try:
        print("ROC-AUC:", roc_auc_score(y_true, y_prob))
    except ValueError as exc:
        print("ROC-AUC: n/a (", exc, ")")


def main():
    _, _, test_ds = load_datasets()
    for name, path in MODEL_FILES.items():
        if not path.exists():
            print(f"\n[skip] {name}: {path} not found.")
            continue
        print(f"\n=== {name} RESULTS ===")
        model = tf.keras.models.load_model(path)
        evaluate_model(model, test_ds)


if __name__ == "__main__":
    main()

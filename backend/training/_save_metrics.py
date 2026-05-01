"""Helper: evaluate a trained model on the test set and save a small JSON metadata file."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)


def evaluate_and_save(model: tf.keras.Model, test_ds, model_key: str, model_path: Path):
    y_true, y_prob = [], []
    for images, labels in test_ds:
        preds = model.predict(images, verbose=0).flatten()
        y_true.extend(labels.numpy().tolist())
        y_prob.extend(preds.tolist())

    y_true = np.array(y_true)
    y_prob = np.array(y_prob)
    y_pred = (y_prob > 0.5).astype(int)

    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_true, y_pred).tolist()
    f1 = f1_score(y_true, y_pred, zero_division=0)
    try:
        roc = float(roc_auc_score(y_true, y_prob))
    except ValueError:
        roc = None

    metrics = {
        "model": model_key,
        "accuracy": report["accuracy"],
        "f1": float(f1),
        "roc_auc": roc,
        "precision": report["weighted avg"]["precision"],
        "recall": report["weighted avg"]["recall"],
        "confusion_matrix": cm,
        "n_test_samples": int(len(y_true)),
    }

    meta_path = model_path.with_suffix(".json")
    meta_path.write_text(json.dumps(metrics, indent=2))
    print(f"Saved metrics -> {meta_path}")
    print(json.dumps(metrics, indent=2))
    return metrics

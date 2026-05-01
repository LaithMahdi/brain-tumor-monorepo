"""Build train/val/test tf.data.Dataset splits — matches the notebook 1:1."""
from __future__ import annotations

import tensorflow as tf

from .config import (
    BATCH_SIZE,
    CLASS_NAMES,
    DATA_DIR,
    IMG_SIZE,
    SEED,
    TRAIN_FRAC,
    VAL_FRAC,
)


def load_datasets():
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Dataset directory not found: {DATA_DIR}\n"
            f"Expected structure: {DATA_DIR}/Benign and {DATA_DIR}/Malignant"
        )

    dataset = tf.keras.utils.image_dataset_from_directory(
        str(DATA_DIR),
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",
        class_names=CLASS_NAMES,
        seed=SEED,
        shuffle=True,
    )

    dataset_size = len(dataset)
    train_size = int(TRAIN_FRAC * dataset_size)
    val_size = int(VAL_FRAC * dataset_size)

    train_ds = dataset.take(train_size)
    remaining = dataset.skip(train_size)
    val_ds = remaining.take(val_size)
    test_ds = remaining.skip(val_size)

    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000, seed=SEED).prefetch(AUTOTUNE)
    val_ds = val_ds.cache().prefetch(AUTOTUNE)
    test_ds = test_ds.cache().prefetch(AUTOTUNE)

    print(f"Total batches: {dataset_size}")
    print(f"  train: {train_size} batches")
    print(f"  val:   {val_size} batches")
    print(f"  test:  {dataset_size - train_size - val_size} batches")

    return train_ds, val_ds, test_ds


def metric_set():
    return [
        "accuracy",
        tf.keras.metrics.Precision(name="precision"),
        tf.keras.metrics.Recall(name="recall"),
        tf.keras.metrics.AUC(name="auc"),
    ]

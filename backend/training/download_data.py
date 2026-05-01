"""Download + sample the Kaggle breast-MRI dataset to backend/data/sampled_dataset.

Reproduces the notebook's preprocessing:
- pulls `abenjelloun/breast-mri-tumor-classification-dataset`
- merges train/val/test
- samples N images per class into a flat Benign/ Malignant/ tree

Set KAGGLE_USERNAME / KAGGLE_KEY env vars before running:

    export KAGGLE_USERNAME=your_user
    export KAGGLE_KEY=your_key
    python -m training.download_data
"""
from __future__ import annotations

import os
import random
import shutil
import zipfile
from pathlib import Path

from .config import BACKEND_DIR, SEED

DATASET_SLUG = "abenjelloun/breast-mri-tumor-classification-dataset"
DATA_ROOT = BACKEND_DIR / "data"
RAW_DIR = DATA_ROOT / "raw"
EXTRACT_DIR = DATA_ROOT / "extracted"
OUTPUT_DIR = DATA_ROOT / "sampled_dataset"
SPLITS = ["train", "val", "test"]
CLASSES = ["Benign", "Malignant"]
N_PER_CLASS = 2000


def main():
    if not (os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY")):
        raise SystemExit(
            "KAGGLE_USERNAME and KAGGLE_KEY env vars are required.\n"
            "See https://www.kaggle.com/docs/api"
        )

    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for cls in CLASSES:
        (OUTPUT_DIR / cls).mkdir(parents=True, exist_ok=True)

    # 1. Download via Kaggle CLI
    print(f"Downloading {DATASET_SLUG} …")
    os.system(f"kaggle datasets download -d {DATASET_SLUG} -p {RAW_DIR}")

    # 2. Find + extract the zip
    zips = list(RAW_DIR.glob("*.zip"))
    if not zips:
        raise SystemExit("No .zip found after Kaggle download.")
    print(f"Extracting {zips[0]} …")
    with zipfile.ZipFile(zips[0], "r") as zf:
        zf.extractall(EXTRACT_DIR)

    base = EXTRACT_DIR / "breast_mri_dataset"
    if not base.exists():
        # fall back if structure differs
        candidates = [p for p in EXTRACT_DIR.iterdir() if p.is_dir()]
        if not candidates:
            raise SystemExit("Couldn't find extracted dataset folder.")
        base = candidates[0]
        print(f"Falling back to base path: {base}")

    # 3. Collect + shuffle + sample
    random.seed(SEED)
    all_images = {cls: [] for cls in CLASSES}
    for split in SPLITS:
        for cls in CLASSES:
            folder = base / split / cls
            if not folder.exists():
                continue
            all_images[cls].extend(p for p in folder.iterdir() if p.is_file())

    for cls in CLASSES:
        random.shuffle(all_images[cls])
        selected = all_images[cls][: min(N_PER_CLASS, len(all_images[cls]))]
        for img_path in selected:
            target = OUTPUT_DIR / cls / f"{cls}_{img_path.name}"
            shutil.copy(img_path, target)
        print(f"{cls} -> {len(selected)} images copied")

    print(f"\nDone. Sampled dataset is at: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

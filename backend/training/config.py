"""Shared training configuration."""
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data" / "sampled_dataset"
SAVED_MODELS_DIR = BACKEND_DIR / "saved_models"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Class names — order MUST match `tf.keras.utils.image_dataset_from_directory`
# which sorts alphabetically. So Benign=0, Malignant=1.
CLASS_NAMES = ["Benign", "Malignant"]

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 5
SEED = 42

# Train/val/test split (matches the notebook: 70/15/15 by batch).
TRAIN_FRAC = 0.70
VAL_FRAC = 0.15

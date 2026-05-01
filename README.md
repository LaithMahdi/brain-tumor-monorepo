# Brain / Breast MRI Tumor Classifier — Monorepo

Full-stack web application that trains and serves **3 deep learning models** for binary tumor classification (Benign vs Malignant):

- **Simple CNN** (3 conv blocks)
- **ResNet50** (transfer learning, ImageNet weights frozen) — labelled "ResNet" in the UI; the upstream notebook used ResNet50 in the "ResNet18" section, so we follow the notebook
- **MLP** (fully connected baseline)

> The notebook this project is based on uses the [breast-mri-tumor-classification-dataset](https://www.kaggle.com/datasets/abenjelloun/breast-mri-tumor-classification-dataset) on Kaggle. The same code/architecture works for any 224×224 RGB binary tumor dataset (rename `Benign` / `Malignant` directories if you swap datasets).

## Repo layout

```
brain-tumor-monorepo/
├── backend/                  # FastAPI inference server + training scripts
│   ├── app/                  # FastAPI app package (the API)
│   ├── training/             # Standalone training scripts (one per model)
│   ├── saved_models/         # .keras files land here after training
│   └── requirements.txt
├── frontend/                 # React + Vite + Tailwind UI
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── package.json              # Top-level scripts (dev, build)
└── README.md
```

## Quick start

### 1. Get the dataset

You need an `images/` folder organised as:

```
backend/data/sampled_dataset/
├── Benign/         (~2000 images)
└── Malignant/      (~2000 images)
```

Either run the helper (requires Kaggle credentials):

```bash
cd backend
export KAGGLE_USERNAME=your_user
export KAGGLE_KEY=your_key
python -m training.download_data
```

…or place your own `Benign/` and `Malignant/` folders under `backend/data/sampled_dataset/`.

### 2. Train the 3 models

```bash
cd backend
pip install -r requirements.txt
python -m training.train_cnn       # → saved_models/cnn.keras
python -m training.train_resnet    # → saved_models/resnet.keras
python -m training.train_mlp       # → saved_models/mlp.keras
python -m training.evaluate        # prints classification reports + ROC-AUC
```

Each script saves the model and a small JSON metadata file with the test metrics.

### 3. Run the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API: `http://localhost:8000/docs`

### 4. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

UI: `http://localhost:5173`

Drag-and-drop an MRI image; the UI calls `POST /api/predict` and shows the Benign/Malignant prediction + confidence from each of the 3 models side by side.

## API

| Method | Path           | Body                | Returns                                                       |
|--------|----------------|---------------------|---------------------------------------------------------------|
| GET    | `/api/health`  | —                   | `{ "status": "ok", "models_loaded": [...] }`                  |
| GET    | `/api/models`  | —                   | List of available models with their saved metrics             |
| POST   | `/api/predict` | `multipart` `image` | `{ "predictions": [{ "model": "cnn", "label": "Malignant", "confidence": 0.93 }, ...] }` |

## Notes

- The backend gracefully skips any model whose `.keras` file is missing, so you can demo with just one model trained.
- All preprocessing matches the notebook: resize to 224×224, RGB, the rescaling layer is *inside* each model, so no manual `/255` is needed at inference.
- "ResNet18" in the notebook markdown was implemented with `tf.keras.applications.ResNet50` (ResNet18 isn't shipped with `tf.keras.applications`). We keep ResNet50 here. If you want a true ResNet18, swap in [`classification_models`](https://github.com/qubvel/classification_models) or implement it manually.

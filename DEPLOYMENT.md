# Deployment Guide — Brain Tumor MRI Classifier

> Full pipeline: local dev → Docker → Kubernetes → GCP (GKE)

---

## 1. Project is ready locally

Verify everything works before containerising:

```bash
# Backend (from brain-tumor-monorepo/backend/)
uvicorn app.main:app --port 8000
# → http://localhost:8000/api/health  should return { "models_loaded": ["cnn","resnet","mlp"] }

# Frontend (from brain-tumor-monorepo/frontend/)
npm run dev
# → http://localhost:5173
```

---

## 2. Docker — three environments

### File map

```
brain-tumor-monorepo/
├── backend/
│   ├── Dockerfile.dev    ← full deps, --reload, debug logs
│   ├── Dockerfile.test   ← adds pytest / httpx
│   └── Dockerfile.prod   ← multi-stage, lean image, 2 workers
├── frontend/
│   ├── Dockerfile.dev    ← Vite dev server
│   ├── Dockerfile.prod   ← Node build → Nginx
│   └── nginx.conf        ← proxies /api to backend, React Router fallback
├── docker-compose.dev.yml
├── docker-compose.test.yml
└── docker-compose.prod.yml
```

### 2a. Development

```bash
docker compose -f docker-compose.dev.yml up --build
```

- Backend → http://localhost:8000  (auto-reload on code save)
- Frontend → http://localhost:5173  (Vite HMR)

### 2b. Tests

```bash
docker compose -f docker-compose.test.yml up --build --exit-code-from backend-test
```

Exit code 0 = all tests passed.

### 2c. Production (local smoke-test)

```bash
docker compose -f docker-compose.prod.yml up --build
```

- App → http://localhost:80  (Nginx serves React + proxies /api)

### Useful Docker commands

```bash
# Build a single image
docker build -f backend/Dockerfile.prod -t brain-tumor-backend:prod ./backend

# Run it standalone
docker run -p 8000:8000 brain-tumor-backend:prod

# Check logs
docker compose -f docker-compose.dev.yml logs -f backend
```

---

## 3. Kubernetes

### File map

```
k8s/
├── namespace.yaml
├── models-pvc.yaml           ← 2 GB persistent volume for .keras files
├── backend/
│   ├── deployment.yaml       ← 2 replicas, RollingUpdate, readiness/liveness probes
│   └── service.yaml          ← ClusterIP (internal)
└── frontend/
    ├── deployment.yaml       ← 2 replicas, RollingUpdate
    └── service.yaml          ← LoadBalancer (external IP from GKE)
```

### Apply locally with minikube (optional)

```bash
minikube start
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/models-pvc.yaml
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/

kubectl get pods -n tumor-classifier
kubectl get services -n tumor-classifier
```

---

## 4. Deploy to GCP (GKE)

### 4a. Prerequisites

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 4b. Enable required APIs

```bash
gcloud services enable \
  container.googleapis.com \
  containerregistry.googleapis.com \
  storage.googleapis.com
```

### 4c. Build & push images to GCR

```bash
# Backend
docker build -f backend/Dockerfile.prod \
  -t gcr.io/YOUR_PROJECT_ID/brain-tumor-backend:latest \
  ./backend
docker push gcr.io/YOUR_PROJECT_ID/brain-tumor-backend:latest

# Frontend
docker build -f frontend/Dockerfile.prod \
  -t gcr.io/YOUR_PROJECT_ID/brain-tumor-frontend:latest \
  ./frontend
docker push gcr.io/YOUR_PROJECT_ID/brain-tumor-frontend:latest
```

### 4d. Create the GKE cluster

```bash
gcloud container clusters create tumor-classifier-cluster \
  --num-nodes=3 \
  --machine-type=e2-standard-4 \
  --region=us-central1
```

### 4e. Connect kubectl to the cluster

```bash
gcloud container clusters get-credentials tumor-classifier-cluster \
  --region=us-central1
```

### 4f. Upload models to a GCS bucket (optional but recommended)

> Avoids baking 1 GB of model files into the Docker image.

```bash
gsutil mb gs://YOUR_PROJECT_ID-models
gsutil cp backend/saved_models/*.keras gs://YOUR_PROJECT_ID-models/
gsutil cp backend/saved_models/*.json  gs://YOUR_PROJECT_ID-models/
```

Then use a Kubernetes init container (or GCS FUSE) to pull the models into the PVC at startup.

### 4g. Deploy to the cluster

Replace `YOUR_PROJECT_ID` in the two `deployment.yaml` files, then:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/models-pvc.yaml
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
```

### 4h. Verify

```bash
kubectl get pods     -n tumor-classifier
kubectl get services -n tumor-classifier
# Note the EXTERNAL-IP of the frontend LoadBalancer service — that's your URL.

kubectl logs -f deployment/backend -n tumor-classifier
```

### 4i. Update a deployment (zero-downtime)

```bash
docker build -f backend/Dockerfile.prod \
  -t gcr.io/YOUR_PROJECT_ID/brain-tumor-backend:v2 ./backend
docker push gcr.io/YOUR_PROJECT_ID/brain-tumor-backend:v2

kubectl set image deployment/backend \
  backend=gcr.io/YOUR_PROJECT_ID/brain-tumor-backend:v2 \
  -n tumor-classifier

kubectl rollout status deployment/backend -n tumor-classifier
```

---

## 5. Quick reference

| Command | Purpose |
|---|---|
| `docker compose -f docker-compose.dev.yml up --build` | Start dev stack |
| `docker compose -f docker-compose.test.yml up --exit-code-from backend-test` | Run tests |
| `docker compose -f docker-compose.prod.yml up --build` | Local prod smoke-test |
| `kubectl apply -f k8s/` | Deploy/update everything on K8s |
| `kubectl rollout undo deployment/backend -n tumor-classifier` | Rollback backend |
| `kubectl scale deployment/backend --replicas=4 -n tumor-classifier` | Scale up |

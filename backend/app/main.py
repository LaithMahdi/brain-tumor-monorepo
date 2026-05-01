"""FastAPI entrypoint.

Run with:
    uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.predict import router as predict_router
from .services.inference import store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    logger.info("Loading saved models …")
    store.load_all()
    logger.info("Loaded models: %s", store.loaded_keys())
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="MRI Tumor Classifier API",
    description="Binary tumor classification (Benign vs Malignant) with 3 deep learning models.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router)


@app.get("/")
def root():
    return {
        "name": "MRI Tumor Classifier API",
        "docs": "/docs",
        "health": "/api/health",
    }

import logging
import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from backend.config import MODEL_PATH

logger = logging.getLogger(__name__)


class ModelService:
    """Singleton wrapper around the trained scikit-learn classifier."""

    _instance: "ModelService | None" = None

    def __new__(cls) -> "ModelService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_loaded", False):
            return
        self._model: Any | None = None
        self._load()
        self._loaded = True

    def _load(self) -> None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
        self._model = joblib.load(MODEL_PATH)
        logger.info("Model loaded from %s", MODEL_PATH)

    def predict(self, features: np.ndarray) -> tuple[str, int]:
        if self._model is None:
            raise RuntimeError("Model is not loaded")

        prediction = self._model.predict(features)[0]
        confidence = 0
        if hasattr(self._model, "predict_proba"):
            confidence = int(max(self._model.predict_proba(features)[0]) * 100)

        return str(prediction), confidence


def get_model_service() -> ModelService:
    return ModelService()

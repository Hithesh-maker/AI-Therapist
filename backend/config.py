import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_ROOT = PROJECT_ROOT / "frontend"

MODEL_PATH = BASE_DIR / "models" / "face_model.pkl"

MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024
MAX_IMAGE_DIMENSION = 320
TARGET_IMAGE_SIZE = (320, 240)
DEFAULT_CONFIDENCE = 0
ALLOWED_ORIGINS = ["*"]

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

API_PREFIX = ""

# Lightweight runtime tuning for free hosting
DETECTOR_CONFIDENCE = 0.5
MAX_FACES = 1

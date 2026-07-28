import base64
import gc
import logging
from typing import Any, Dict

import cv2
import numpy as np
from flask import Blueprint, jsonify, request, render_template

from backend.config import MAX_IMAGE_DIMENSION, MAX_IMAGE_SIZE_BYTES, TARGET_IMAGE_SIZE
from backend.services.detector import get_detector
from backend.services.model_service import get_model_service
from backend.services.voice_service import VoiceService

logger = logging.getLogger(__name__)

bp = Blueprint("main", __name__)


@bp.get("/")
def index() -> str:
    return render_template("index.html")


@bp.get("/health")
def health() -> tuple[Any, int]:
    try:
        detector = get_detector()
        detector.load()
        model_service = get_model_service()
        return jsonify({
            "success": True,
            "status": "ok",
            "model_loaded": True,
            "detector_loaded": detector._loaded,
            "backend": "alive",
        }), 200
    except Exception as exc:  # pragma: no cover - defensive path
        logger.exception("Health check failed")
        return jsonify({"success": False, "error": str(exc)}), 503


@bp.get("/version")
def version() -> tuple[Any, int]:
    return jsonify({"success": True, "version": "2.0.0"}), 200


@bp.post("/predict")
def predict() -> tuple[Any, int]:
    try:
        payload = request.get_json(silent=True) or {}
        image_data = payload.get("image")
        if not image_data:
            return jsonify({"success": False, "error": "No image provided"}), 400

        if len(image_data) > MAX_IMAGE_SIZE_BYTES:
            return jsonify({"success": False, "error": "Image too large"}), 413

        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if image is None:
            return jsonify({"success": False, "error": "Invalid image"}), 400

        height, width = image.shape[:2]
        if max(height, width) > MAX_IMAGE_DIMENSION:
            scale = MAX_IMAGE_DIMENSION / max(height, width)
            new_width = max(1, int(width * scale))
            new_height = max(1, int(height * scale))
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        detector = get_detector()
        detection = detector.detect(image)
        if detection is None:
            return jsonify({"success": True, "emotion": "No Face", "score": 0}), 200

        _, face_crop = detection
        face_crop = cv2.resize(face_crop, TARGET_IMAGE_SIZE, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
        features = gray.flatten().astype(np.float32).reshape(1, -1)

        model_service = get_model_service()
        emotion, confidence = model_service.predict(features)

        del image
        del image_bytes
        del np_arr
        gc.collect()

        return jsonify({"success": True, "emotion": emotion, "score": confidence}), 200

    except Exception as exc:
        logger.exception("Face prediction failed")
        return jsonify({"success": False, "error": str(exc)}), 500


@bp.post("/predict_voice")
def predict_voice() -> tuple[Any, int]:
    try:
        audio_file = request.files.get("audio")
        if not audio_file:
            return jsonify({"success": False, "error": "No audio provided"}), 400

        voice_service = VoiceService()
        result = voice_service.predict(audio_file.read())
        return jsonify({"success": True, **result}), 200
    except Exception as exc:
        logger.exception("Voice prediction failed")
        return jsonify({"success": False, "error": str(exc)}), 500

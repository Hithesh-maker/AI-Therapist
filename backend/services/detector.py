import cv2
import numpy as np
from typing import Optional, Tuple

from backend.config import DETECTOR_CONFIDENCE, MAX_FACES, TARGET_IMAGE_SIZE


class LightweightFaceDetector:
    """CPU-friendly face detector that preserves a single-face feature vector."""

    def __init__(self) -> None:
        self._detector = None
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return

        detector = cv2.FaceDetectorYN_create(
            "",  # model path; using the default built-in cascade path if available
            "",
            (1, 1),
        )
        self._detector = detector
        self._loaded = True

    def detect(self, image: np.ndarray) -> Optional[Tuple[Tuple[int, int, int, int], np.ndarray]]:
        if not self._loaded:
            self.load()

        resized = cv2.resize(image, TARGET_IMAGE_SIZE)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        faces = []

        # Use a simple Haar cascade fallback when OpenCV's DNN backend is unavailable.
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        detected = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(detected) > 0:
            x, y, w, h = detected[0]
            faces.append((x, y, w, h))

        if not faces:
            return None

        bbox = faces[0]
        x, y, w, h = bbox
        crop = resized[y:y + h, x:x + w]
        if crop.size == 0:
            return None
        return bbox, crop


_detector = LightweightFaceDetector()


def get_detector() -> LightweightFaceDetector:
    return _detector

import pickle
from pathlib import Path

import cv2
import numpy as np

from utils.face_detection import load_image_from_bytes, preprocess_face

BASE_DIR = Path(__file__).resolve().parents[1]
ENCODINGS_PATH = BASE_DIR / "encodings" / "face_encodings.pkl"
FACE_DATA_DIR = BASE_DIR / "face_data"


def _save_encodings(encodings):
    ENCODINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ENCODINGS_PATH, "wb") as handle:
        pickle.dump(encodings, handle)


def _read_encodings():
    if not ENCODINGS_PATH.exists():
        return {}

    try:
        with open(ENCODINGS_PATH, "rb") as handle:
            data = pickle.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _embedding_from_image(image):
    return preprocess_face(image)


def train_face_encodings():
    encodings = {}

    for student_dir in FACE_DATA_DIR.iterdir():
        if not student_dir.is_dir():
            continue

        student_id = student_dir.name
        embeddings = []

        for image_path in student_dir.iterdir():
            if not image_path.is_file():
                continue
            if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".bmp"}:
                continue

            image = cv2.imread(str(image_path))
            if image is None:
                continue

            embedding = _embedding_from_image(image)
            if embedding is not None:
                embeddings.append(embedding)

        if embeddings:
            encodings[student_id] = np.mean(np.vstack(embeddings), axis=0)

    _save_encodings(encodings)
    return encodings


def recognize_face_from_bytes(image_bytes):
    try:
        image = load_image_from_bytes(image_bytes)
    except ValueError:
        return None

    probe = _embedding_from_image(image)
    if probe is None:
        return None

    encodings = _read_encodings()
    if not encodings:
        return None

    best_student = None
    best_distance = float("inf")

    for student_id, stored_embedding in encodings.items():
        distance = float(np.linalg.norm(probe - stored_embedding))
        if distance < best_distance:
            best_student = student_id
            best_distance = distance

    threshold = 22.0
    if best_student is not None and best_distance <= threshold:
        confidence = max(0.0, 1.0 - (best_distance / threshold))
        return {
            "student_id": best_student,
            "confidence": round(float(confidence), 4),
        }

    return None

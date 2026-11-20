from io import BytesIO

import cv2
import numpy as np
from PIL import Image


CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_CASCADE = cv2.CascadeClassifier(CASCADE_PATH)


def load_image_from_bytes(image_bytes):
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not read uploaded image")
    return image


def detect_faces(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )
    return faces


def crop_face(image):
    faces = detect_faces(image)
    if len(faces) == 0:
        return None

    x, y, w, h = faces[0]
    return image[y : y + h, x : x + w]


def preprocess_face(image):
    face = crop_face(image)
    if face is None:
        return None

    face = cv2.resize(face, (128, 128))
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    normalized = gray.astype(np.float32) / 255.0
    return normalized.flatten()

import numpy as np
from insightface.app import FaceAnalysis

_face_app = None


def get_face_app():
    """
    Returns a single shared FaceAnalysis instance (loaded once, reused everywhere).
    Avoids reloading the buffalo_l model on every call.
    """
    global _face_app
    if _face_app is None:
        _face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        _face_app.prepare(ctx_id=0)
    return _face_app


def get_embedding_from_image(img):
    """
    Takes an OpenCV image (numpy array, as returned by cv2.imread or a webcam frame).
    Returns (embedding, face_count).
    - embedding: 512-dim numpy array of the FIRST detected face, or None if no face found.
    - face_count: number of faces detected in the image.
    """
    app = get_face_app()
    faces = app.get(img)
    if not faces:
        return None, 0
    return faces[0].embedding, len(faces)


def cosine_similarity(embedding1, embedding2):
    """Returns similarity score between -1 and 1. Higher = more similar."""
    return float(
        np.dot(embedding1, embedding2) /
        (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    )


# Recognition threshold: similarity >= this value = considered a match.
# Based on our own testing: same-person ~0.94, different-person ~0.06.
RECOGNITION_THRESHOLD = 0.45

"""
recognize.py - Module nhan dien khuon mat (Slot 1)
==================================================

Cung cap ham recognize_frame(frame) duoc dung boi main.py.
Co the chay truc tiep file nay de test nhan dien khong ghi DB.

CHAY (test):
    python recognize.py
"""

import cv2
import pickle
import os
import face_recognition
import numpy as np
import config


# Load model 1 lan khi import
if not os.path.exists(config.MODEL_PATH):
    raise FileNotFoundError(
        f"Khong tim thay {config.MODEL_PATH}. "
        f"Chay 'python encode_faces.py' truoc."
    )

with open(config.MODEL_PATH, "rb") as f:
    _data = pickle.load(f)

_known_encodings = _data["encodings"]
_known_names = _data["names"]

print(f"[Slot1] Loaded {len(_known_encodings)} face encodings "
      f"({len(set(_known_names))} people)")


def recognize_frame(frame):
    """
    Input:
        frame: BGR image from OpenCV

    Output:
        List of tuples: [(name, (top, right, bottom, left)), ...]
        name la "Unknown" neu khong match.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame, model="hog")
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    results = []
    for face_encoding, face_location in zip(face_encodings, face_locations):
        name = "Unknown"

        if len(_known_encodings) > 0:
            distances = face_recognition.face_distance(_known_encodings, face_encoding)
            best_match_index = np.argmin(distances)
            best_distance = distances[best_match_index]

            if best_distance < config.RECOGNITION_THRESHOLD:
                name = _known_names[best_match_index]

        results.append((name, face_location))

    return results


def _test_standalone():
    """Test nhan dien thuan (khong ghi DB, khong hardware)."""
    cap = cv2.VideoCapture(config.CAM_INDEX)
    if not cap.isOpened():
        raise RuntimeError(
            f"Khong mo duoc webcam (index={config.CAM_INDEX}). "
            f"Thu doi CAM_INDEX trong config.py."
        )

    print("Standalone test - khong ghi DB, khong gui hardware.")
    print("An 'q' de thoat.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = recognize_frame(frame)
        for name, (top, right, bottom, left) in results:
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Face Recognition (test mode)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    _test_standalone()

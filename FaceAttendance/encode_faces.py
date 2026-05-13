"""
encode_faces.py - Encode dataset thanh vector dac trung (Slot 1)
================================================================

CHAY:
    python encode_faces.py

Yeu cau:
    - Da chay capture_images.py truoc do, co anh trong dataset/<ten>/

Ket qua:
    - File models/known_faces.pkl chua encodings + names
"""

import os
import pickle
import cv2
import face_recognition
import config

os.makedirs(os.path.dirname(config.MODEL_PATH), exist_ok=True)

known_encodings = []
known_names = []

if not os.path.isdir(config.DATASET_DIR):
    print(f"Khong tim thay folder dataset/. Chay capture_images.py truoc.")
    raise SystemExit(1)

people = [p for p in os.listdir(config.DATASET_DIR)
          if os.path.isdir(os.path.join(config.DATASET_DIR, p))]

if not people:
    print(f"Folder dataset/ rong. Chay capture_images.py truoc.")
    raise SystemExit(1)

print(f"Tim thay {len(people)} nguoi trong dataset: {people}")
print("=" * 60)

for person_name in people:
    person_dir = os.path.join(config.DATASET_DIR, person_name)
    print(f"Encoding: {person_name}")

    person_count = 0
    for filename in os.listdir(person_dir):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(person_dir, filename)
        image_bgr = cv2.imread(image_path)
        if image_bgr is None:
            print(f"  Cannot read: {image_path}")
            continue

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(image_rgb, model="hog")
        face_encodings = face_recognition.face_encodings(image_rgb, face_locations)

        if len(face_encodings) == 0:
            print(f"  No face: {filename}")
            continue
        if len(face_encodings) > 1:
            print(f"  Multiple faces, using first: {filename}")

        known_encodings.append(face_encodings[0])
        known_names.append(person_name)
        person_count += 1

    print(f"  -> {person_count} anh OK cho {person_name}")

print("=" * 60)
print(f"Tong cong: {len(known_encodings)} faces tu {len(set(known_names))} nguoi")

data = {"encodings": known_encodings, "names": known_names}
with open(config.MODEL_PATH, "wb") as f:
    pickle.dump(data, f)

print(f"Saved: {config.MODEL_PATH}")
print(f"Buoc tiep theo: chay 'python main.py' de test nhan dien")

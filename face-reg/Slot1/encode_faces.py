import os
import pickle
import cv2
import face_recognition

DATASET_DIR = "dataset"
MODEL_DIR = "models"
OUTPUT_PATH = os.path.join(MODEL_DIR, "known_faces.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

known_encodings = []
known_names = []

for person_name in os.listdir(DATASET_DIR):
    person_dir = os.path.join(DATASET_DIR, person_name)

    if not os.path.isdir(person_dir):
        continue

    print(f"Encoding: {person_name}")

    for filename in os.listdir(person_dir):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(person_dir, filename)

        image_bgr = cv2.imread(image_path)
        if image_bgr is None:
            print(f"Cannot read image: {image_path}")
            continue

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(image_rgb, model="hog")
        face_encodings = face_recognition.face_encodings(image_rgb, face_locations)

        if len(face_encodings) == 0:
            print(f"No face found: {image_path}")
            continue

        if len(face_encodings) > 1:
            print(f"More than one face found, using first face: {image_path}")

        known_encodings.append(face_encodings[0])
        known_names.append(person_name)

print(f"Total encoded faces: {len(known_encodings)}")

data = {
    "encodings": known_encodings,
    "names": known_names
}

with open(OUTPUT_PATH, "wb") as f:
    pickle.dump(data, f)

print(f"Saved encodings to {OUTPUT_PATH}")
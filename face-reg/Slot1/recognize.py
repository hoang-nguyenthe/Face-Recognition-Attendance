import cv2
import pickle
import face_recognition
import numpy as np

MODEL_PATH = "models/known_faces.pkl"
THRESHOLD = 0.45

with open(MODEL_PATH, "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_names = data["names"]


def recognize_frame(frame):
    """
    Input:
        frame: BGR image from OpenCV

    Output:
        List of tuples:
        [
            (name, (top, right, bottom, left)),
            ...
        ]
    """

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame, model="hog")
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    results = []

    for face_encoding, face_location in zip(face_encodings, face_locations):
        name = "Unknown"

        if len(known_encodings) > 0:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = np.argmin(distances)
            best_distance = distances[best_match_index]

            if best_distance < THRESHOLD:
                name = known_names[best_match_index]

        results.append((name, face_location))

    return results


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Khong mo duoc webcam")

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        results = recognize_frame(frame)

        for name, (top, right, bottom, left) in results:
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(
                frame,
                name,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

        cv2.imshow("Face Recognition Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
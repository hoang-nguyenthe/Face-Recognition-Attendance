"""
recognize_with_attendance.py
============================
File tich hop giua Slot 1 (recognize.py) va Slot 2 (db.py).

Khac voi recognize.py goc cua Slot 1, file nay tu dong ghi diem danh
vao DB moi khi nhan dien duoc khuon mat.

CHAY:
    python recognize_with_attendance.py

YEU CAU:
    - File nay phai cung thu muc voi: recognize.py, db.py
    - Da chay encode_faces.py truoc do (de co models/known_faces.pkl)
    - Tat ca thanh vien da co trong dataset

TUONG TAC:
    - Nhin vao webcam, he thong se nhan dien va ghi diem danh.
    - Trong gov 5 phut neu cung 1 nguoi xuat hien lai, KHONG ghi lai (cooldown).
    - Console se in ra khi diem danh thanh cong / bi block.
    - An 'q' de thoat.

LIEN HE NHOM:
    Slot 2 (Hoang) - Backend
"""

import cv2
import time
from recognize import recognize_frame  # tu Slot 1
import db                              # tu Slot 2 (cung thu muc)


# Mau sac (BGR) cho hien thi
GREEN = (0, 255, 0)
RED = (0, 0, 255)
YELLOW = (0, 200, 255)


def draw_label(frame, text, location, color):
    """Ve box + label tren frame."""
    top, right, bottom, left = location
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    cv2.putText(
        frame, text, (left, top - 10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
    )


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Khong mo duoc webcam")

    print("=" * 60)
    print("FACE RECOGNITION ATTENDANCE - NHOM 31")
    print("=" * 60)
    print("An 'q' de thoat.")
    print("Cooldown: 5 phut/nguoi.")
    print("=" * 60)

    # Tracking de khong in log spam
    last_logged_status = {}  # name -> ("success"|"cooldown", timestamp)

    # Throttle: chay recognize_frame moi N frames de do FPS
    frame_count = 0
    RECOGNIZE_EVERY = 3  # cu 3 frame moi nhan dien 1 lan
    last_results = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Throttle: chi nhan dien 1/3 frame de tang FPS
        if frame_count % RECOGNIZE_EVERY == 0:
            last_results = recognize_frame(frame)

            # Goi db.mark_attendance cho moi khuon mat nhan dien duoc
            for name, location in last_results:
                if name == "Unknown":
                    continue

                result = db.mark_attendance(name)

                # In log gon - chi in khi trang thai thay doi
                status = "success" if result["success"] else "cooldown"
                prev = last_logged_status.get(name)
                if prev != status:
                    if result["success"]:
                        print(f"[OK]   {result['timestamp']} - {name} - Diem danh thanh cong")
                    else:
                        print(f"[SKIP] {name} - {result['message']}")
                    last_logged_status[name] = status

        # Ve box tren frame (dung last_results de mooth)
        for name, location in last_results:
            if name == "Unknown":
                draw_label(frame, "Unknown", location, RED)
            else:
                draw_label(frame, name, location, GREEN)

        # Hien thi info goc duoi
        cv2.putText(
            frame, "Press Q to quit",
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, YELLOW, 2
        )

        cv2.imshow("Face Recognition Attendance - Nhom 31", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Tom tat
    print("\n" + "=" * 60)
    print("TOM TAT PHIEN")
    print("=" * 60)
    stats = db.get_stats()
    print(f"Tong so nguoi diem danh hom nay: {stats['today_count']}")
    print(f"Som nhat: {stats['earliest_today']}")
    print(f"Muon nhat: {stats['latest_today']}")
    print("=" * 60)


if __name__ == "__main__":
    main()

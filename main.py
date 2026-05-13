"""
main.py - File CHINH chay he thong diem danh
============================================
TICH HOP TOAN BO:
    Slot 1 (recognize.py)  - nhan dien khuon mat
    Slot 2 (db.py)         - ghi DB voi cooldown
    Slot 4 (hardware.py)   - tin hieu LED/buzzer/LCD

Slot 3 (dashboard.py) chay rieng o terminal khac, tu doc DB len.

CHAY:
    python main.py

YEU CAU TRUOC KHI CHAY:
    1. Da cai du package (pip install -r requirements.txt)
    2. Da chup dataset (python capture_images.py) cho moi nguoi
    3. Da encode (python encode_faces.py) -> co models/known_faces.pkl
    4. (Tuy chon) Da nap slot4_system.ino vao Arduino

TUONG TAC:
    - Nhin webcam: nhan dien + ghi DB + bao LED/buzzer
    - Cooldown 5 phut/nguoi (khong ghi trung)
    - LED xanh = thanh cong, LED do = unknown
    - Nhan 'q' de thoat (in tom tat phien)
"""

import cv2
import time
import config
from recognize import recognize_frame
import db
from hardware import HardwareController


# Mau sac BGR cho overlay
GREEN = (0, 255, 0)
RED = (0, 0, 255)
YELLOW = (0, 200, 255)
WHITE = (255, 255, 255)


def draw_label(frame, text, location, color):
    """Ve box quanh khuon mat va text ten."""
    top, right, bottom, left = location
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    # Nen den phia sau text de de doc
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    cv2.rectangle(frame, (left, top - th - 12), (left + tw + 6, top), color, cv2.FILLED)
    cv2.putText(frame, text, (left + 3, top - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)


def draw_overlay(frame, fps, last_event):
    """Ve thong tin overlay goc man hinh."""
    h, w = frame.shape[:2]
    # Goc trai tren: status
    cv2.putText(frame, "Nhom 31 - Face Attendance",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
    cv2.putText(frame, f"FPS: {fps:.1f}",
                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)

    # Goc trai duoi: huong dan
    cv2.putText(frame, "Press Q to quit",
                (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 1)

    # Goc phai tren: event gan day
    if last_event:
        text = last_event[:40]
        (tw, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.putText(frame, text,
                    (w - tw - 10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN, 1)


def main():
    print("=" * 60)
    print("FACE RECOGNITION ATTENDANCE SYSTEM - NHOM 31 - HK252")
    print("=" * 60)

    # 1. Khoi tao hardware
    hw = HardwareController()

    # 2. Mo webcam
    cap = cv2.VideoCapture(config.CAM_INDEX)
    if not cap.isOpened():
        hw.close()
        raise RuntimeError(
            f"Khong mo duoc webcam (CAM_INDEX={config.CAM_INDEX}). "
            f"Sua trong config.py hoac set bien moi truong CAM_INDEX=1"
        )

    print(f"[Cam] Mo webcam index={config.CAM_INDEX}")
    print(f"[AI]  Threshold={config.RECOGNITION_THRESHOLD}, "
          f"recognize moi {config.RECOGNIZE_EVERY_N_FRAMES} frame")
    print(f"[DB]  Cooldown {config.ATTENDANCE_COOLDOWN_MINUTES} phut/nguoi")
    print("=" * 60)
    print("BAT DAU. Nhan 'q' tren cua so video de thoat.")
    print("=" * 60)

    # 3. State
    last_logged_status = {}  # name -> "success" | "cooldown"
    last_results = []
    frame_count = 0
    last_event_text = ""

    # FPS tracking
    fps_t0 = time.time()
    fps_n = 0
    fps_display = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[Cam] Loi doc frame, thoat.")
                break

            frame_count += 1
            fps_n += 1

            # Throttle: chay recognize moi N frame
            if frame_count % config.RECOGNIZE_EVERY_N_FRAMES == 0:
                last_results = recognize_frame(frame)

                # Xu ly tung khuon mat trong frame
                has_known = False
                has_unknown = False

                for name, location in last_results:
                    if name == "Unknown":
                        has_unknown = True
                        continue

                    has_known = True
                    result = db.mark_attendance(name)
                    status = "success" if result["success"] else "cooldown"
                    prev = last_logged_status.get(name)

                    # Chi log + gui HW khi trang thai THAY DOI (khong spam)
                    if prev != status:
                        if result["success"]:
                            msg = f"[OK]   {result['timestamp']} - {name} - Diem danh OK"
                            print(msg)
                            last_event_text = f"OK: {name} @ {result['timestamp']}"
                            hw.signal_success(name)
                        else:
                            msg = f"[SKIP] {name} - {result['message']}"
                            print(msg)
                            last_event_text = f"SKIP: {name}"
                        last_logged_status[name] = status

                # Neu chi co Unknown (khong co ai duoc nhan dien) -> bao do
                # HardwareController da co throttle nen khong spam
                if has_unknown and not has_known:
                    hw.signal_unknown()

            # Ve box len frame (dung last_results de muot)
            for name, location in last_results:
                if name == "Unknown":
                    draw_label(frame, "Unknown", location, RED)
                else:
                    draw_label(frame, name, location, GREEN)

            # FPS
            if fps_n >= 30:
                now = time.time()
                fps_display = fps_n / (now - fps_t0)
                fps_t0 = now
                fps_n = 0

            draw_overlay(frame, fps_display, last_event_text)

            cv2.imshow("Face Recognition Attendance - Nhom 31", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\n[Main] Ctrl+C - thoat...")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        hw.close()

        # Tom tat phien
        print("\n" + "=" * 60)
        print("TOM TAT PHIEN")
        print("=" * 60)
        stats = db.get_stats()
        print(f"  Tong so nguoi diem danh hom nay: {stats['today_count']}")
        print(f"  Tong luot ghi hom nay:           {stats['today_total']}")
        print(f"  Som nhat:                        {stats['earliest_today'] or '--'}")
        print(f"  Muon nhat:                       {stats['latest_today'] or '--'}")
        print("=" * 60)


if __name__ == "__main__":
    main()

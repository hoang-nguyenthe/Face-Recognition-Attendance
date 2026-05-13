"""
capture_images.py - Chup anh dataset (Slot 1)
=============================================

CHAY:
    python capture_images.py

Yeu cau:
    - Webcam ket noi va hoat dong
    - Tao folder dataset/<ten_nguoi>/ va luu 30 anh

LUU Y QUAN TRONG:
    Ten nhap o day se la ten hien thi khi diem danh va luu vao DB.
    Khuyen nghi dung ten ngan, KHONG dau: "Hoang", "Long", "Quan", "Thanh".
"""

import cv2
import os
import time
import config

name = input("Nhap ten nguoi chup (ngan, khong dau, vd: Hoang): ").strip()
if not name:
    print("Ten rong. Thoat.")
    raise SystemExit(1)

save_dir = os.path.join(config.DATASET_DIR, name)
os.makedirs(save_dir, exist_ok=True)

cap = cv2.VideoCapture(config.CAM_INDEX)
if not cap.isOpened():
    raise RuntimeError(
        f"Khong mo duoc webcam (index={config.CAM_INDEX}). "
        f"Thu doi CAM_INDEX trong config.py (0 hoac 1)."
    )

print("Dang khoi dong camera...")
time.sleep(2)

# Warm-up camera
for _ in range(30):
    cap.read()

count = 0
MAX_IMAGES = 30
print(f"Bat dau chup {MAX_IMAGES} anh cho {name}")
print("Dat mat o giua camera, anh sang tot, nhin thang.")
print("An 'q' de thoat som.")

while count < MAX_IMAGES:
    ret, frame = cap.read()
    if not ret:
        print("Khong doc duoc frame")
        continue

    # Hien thi so anh da chup
    display = frame.copy()
    cv2.putText(display, f"Chup {count + 1}/{MAX_IMAGES}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(display, "Nhin thang vao camera", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    cv2.imshow("Capture Dataset - Press Q to quit", display)

    img_path = os.path.join(save_dir, f"{count:03d}.jpg")
    cv2.imwrite(img_path, frame)
    count += 1
    print(f"Saved {img_path}")

    time.sleep(0.2)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print(f"Xong. Da chup {count} anh cho {name}")
print(f"Buoc tiep theo: chay 'python encode_faces.py'")

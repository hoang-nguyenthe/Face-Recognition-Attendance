import cv2
import os
import time

name = input("Nhap ten nguoi chup: ").strip()
save_dir = os.path.join("dataset", name)
os.makedirs(save_dir, exist_ok=True)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Khong mo duoc webcam")

print("Dang khoi dong camera...")
time.sleep(2)

# Warm-up camera: bo qua vai frame dau
for _ in range(30):
    cap.read()

count = 0
max_images = 30

print(f"Bat dau chup {max_images} anh cho {name}")
print("Dat mat o giua camera, anh sang tot, nhin thang.")

while count < max_images:
    ret, frame = cap.read()

    if not ret:
        print("Khong doc duoc frame")
        continue

    cv2.imshow("Capture Dataset - Press Q to quit", frame)

    key = cv2.waitKey(1) & 0xFF

    img_path = os.path.join(save_dir, f"{count:03d}.jpg")
    cv2.imwrite(img_path, frame)

    print(f"Saved {img_path}")
    count += 1

    time.sleep(0.2)

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print(f"Xong. Da chup {count} anh cho {name}")
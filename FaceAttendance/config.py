"""
config.py - Cau hinh trung tam cho he thong
Nhom 31 - HK252

Moi file khac import config nay. Sua o day mot lan, khong can sua nhieu noi.

Co the override bang bien moi truong:
    set CAM_INDEX=1
    set ARDUINO_PORT=COM5
    python main.py
"""

import os

# ============== CAMERA ==============
# Camera index: 0 = webcam mac dinh, 1 = webcam thu 2 (neu laptop co camera tich hop)
# Neu khong mo duoc camera, thu doi giua 0 va 1.
CAM_INDEX = int(os.environ.get("CAM_INDEX", "0"))

# ============== AI / RECOGNITION ==============
# Threshold khoang cach. Cang nho = cang chat (it nham nhung de unknown).
# 0.45 la can bang tot. Neu hay bi unknown -> tang len 0.50.
# Neu hay bi nham nguoi nay voi nguoi khac -> giam xuong 0.40.
RECOGNITION_THRESHOLD = float(os.environ.get("RECOGNITION_THRESHOLD", "0.45"))

# Chay nhan dien moi N frame de tang FPS (3 = ~10fps recognize tren cam 30fps)
RECOGNIZE_EVERY_N_FRAMES = 3

# ============== PATHS ==============
MODEL_PATH = "models/known_faces.pkl"
DATASET_DIR = "dataset"
DB_PATH = os.environ.get("ATTENDANCE_DB", "attendance.db")

# ============== BACKEND ==============
BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = int(os.environ.get("BACKEND_PORT", "5000"))
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"

# ============== HARDWARE (Slot 4) ==============
# COM port cua Arduino:
#   Windows: COM3, COM4, COM7...
#   Linux:   /dev/ttyUSB0, /dev/ttyACM0
#   macOS:   /dev/cu.usbmodem*
# De trong "" hoac dat HARDWARE_ENABLED=False neu khong co Arduino.
ARDUINO_PORT = os.environ.get("ARDUINO_PORT", "COM7")
ARDUINO_BAUD = 9600

# Bat/tat phan cung. Khi tat se in tin hieu ra console thay vi gui Arduino.
HARDWARE_ENABLED = os.environ.get("HARDWARE_ENABLED", "auto").lower()
# Cac gia tri: "true" (bat buoc dung HW), "false" (tat hoan toan), "auto" (tu fallback neu khong ket noi duoc)

# Khoang thoi gian toi thieu giua 2 lan gui tin hieu R (Unknown).
# Tranh spam buzzer khi mat la trong frame lien tuc.
HARDWARE_UNKNOWN_COOLDOWN_SEC = 3.0

# ============== ATTENDANCE LOGIC ==============
# Cooldown giua 2 lan diem danh cua cung 1 nguoi (phut).
ATTENDANCE_COOLDOWN_MINUTES = 5

# ============== DASHBOARD ==============
DASHBOARD_AUTO_REFRESH_SEC = 5  # Tu refresh moi 5 giay

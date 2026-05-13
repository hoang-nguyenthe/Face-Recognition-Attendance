# Hệ thống Điểm danh Nhận diện Khuôn mặt — Nhóm 31

**Face Recognition Attendance System** | Đồ án Đa ngành CS × CE | HK252 — ĐH Bách Khoa TP.HCM

Hệ thống điểm danh tự động qua webcam, ghi vào SQLite, hiển thị web dashboard, phản hồi bằng LED/buzzer/LCD qua Arduino.

---

## 📁 Cấu trúc thư mục

```
FaceAttendance-Nhom31/
├── config.py                  # Cấu hình trung tâm (sửa 1 nơi, áp dụng tất cả)
├── requirements.txt           # Danh sách thư viện Python
│
├── capture_images.py          # Slot 1: chụp ảnh dataset
├── encode_faces.py            # Slot 1: encode ảnh → known_faces.pkl
├── recognize.py               # Slot 1: hàm recognize_frame() + test standalone
│
├── db.py                      # Slot 2: SQLite (mark_attendance, get_today, stats)
├── app.py                     # Slot 2: Flask REST API (port 5000)
├── register_team.py           # Slot 2: đăng ký 4 thành viên vào bảng students
├── test_api.py                # Slot 2: test tự động các endpoint
│
├── dashboard.py               # Slot 3: Streamlit dashboard (port 8501), auto-refresh
│
├── hardware.py                # Slot 4: HardwareController (auto-fallback console)
├── arduino/
│   ├── SLOT4_README.md        # Hướng dẫn chi tiết phần cứng
│   ├── serial_test.py         # Test Arduino bằng tay
│   └── slot4_system/
│       └── slot4_system.ino   # Code nạp vào Arduino Uno
│
├── main.py                    # ⭐ FILE CHÍNH: tích hợp Slot 1+2+4
├── run_all.py                 # Launcher: chạy main + dashboard 1 lệnh
├── test_integration.py        # Test logic tích hợp (không cần camera/HW)
│
├── dataset/                   # Ảnh khuôn mặt (sinh ra từ capture_images.py)
│   ├── Hoang/000.jpg ... 029.jpg
│   ├── Long/...
│   ├── Quan/...
│   └── Thanh/...
└── models/
    └── known_faces.pkl        # Encodings (sinh ra từ encode_faces.py)
```

---

## ⚙️ Cài đặt (làm 1 lần)

### Bước 1. Cài Python 3.10+

```bash
python --version    # phải >= 3.10
```

### Bước 2. Tạo venv và cài thư viện

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

> ⚠️ **Lưu ý cài `dlib` (dependency của `face_recognition`) trên Windows:**
> - Cách dễ nhất: `conda install -c conda-forge dlib` rồi mới `pip install face_recognition`
> - Hoặc dùng WSL2 (Ubuntu trong Windows)
> - Hoặc cài Visual C++ Build Tools trước rồi `pip install dlib`

### Bước 3. Sửa `config.py` cho phù hợp máy

Mở `config.py` và sửa các giá trị:

| Biến | Ý nghĩa | Khi nào sửa |
|------|---------|-------------|
| `CAM_INDEX` | Số thứ tự webcam (0 hoặc 1) | Nếu mở camera không lên, đổi 0 ↔ 1 |
| `ARDUINO_PORT` | Cổng Arduino: `COM7` (Win), `/dev/ttyUSB0` (Linux) | Xem trong Arduino IDE → Tools → Port |
| `HARDWARE_ENABLED` | `"auto"`, `"true"`, `"false"` | `false` nếu demo không có Arduino |
| `RECOGNITION_THRESHOLD` | 0.45 là cân bằng | Tăng (→0.50) nếu hay bị Unknown; giảm (→0.40) nếu hay nhầm |

---

## 🚀 Cách chạy

### 🟢 Lần đầu tiên: chuẩn bị dữ liệu (làm 1 lần)

**Bước 1.** Chụp ảnh cho từng thành viên (mỗi người ~30s)

```bash
python capture_images.py
# Nhập tên: Hoang     → tạo dataset/Hoang/000.jpg ... 029.jpg
python capture_images.py
# Nhập tên: Long
python capture_images.py
# Nhập tên: Quan
python capture_images.py
# Nhập tên: Thanh
```

> ⚠️ Dùng **tên ngắn không dấu** (Hoang, Long, Quan, Thanh) — tên này hiển thị khi điểm danh và lưu DB.

**Bước 2.** Encode toàn bộ dataset

```bash
python encode_faces.py
# Tạo ra: models/known_faces.pkl
```

**Bước 3.** (Tùy chọn) Đăng ký thông tin sinh viên vào bảng `students`

```bash
python register_team.py
```

**Bước 4.** (Tùy chọn) Nạp Arduino: mở `arduino/slot4_system/slot4_system.ino` trong Arduino IDE → Upload

---

### 🎬 Mỗi lần demo: chạy hệ thống

**Cách 1 — Một lệnh chạy tất cả (khuyến nghị):**

```bash
python run_all.py
```

Sẽ tự động mở:
- Cửa sổ OpenCV với camera
- Dashboard tại http://localhost:8501 (mở trình duyệt thủ công)

**Cách 2 — Chạy thủ công (2 terminal):**

```bash
# Terminal 1
python main.py

# Terminal 2 (mở thêm)
streamlit run dashboard.py
```

**Cách 3 — Đầy đủ 3 process (đúng kiến trúc client-server):**

```bash
# Terminal 1: Backend API
python app.py

# Terminal 2: Camera + AI
python main.py

# Terminal 3: Dashboard (sửa USE_API=True trong dashboard.py)
streamlit run dashboard.py
```

---

## 🧪 Kiểm thử trước demo

### Test 1 — Logic tích hợp (không cần camera/Arduino)

```bash
python test_integration.py
```

Kiểm tra: DB, cooldown, hardware throttle, pipeline đầy đủ.
**Phải đạt 19/19 PASS.**

### Test 2 — REST API (cần app.py chạy)

```bash
# Terminal 1
python app.py
# Terminal 2
python test_api.py
```

**Phải đạt 23/23 PASS.**

### Test 3 — Nhận diện thuần (không ghi DB, không HW)

```bash
python recognize.py
```

Đứng trước camera, phải thấy tên hiển thị đúng + khung xanh.

### Test 4 — Arduino (cần Arduino cắm)

```bash
python arduino/serial_test.py
# Nhập 1 → đèn xanh, beep ngắn, LCD "Welcome"
# Nhập 0 → đèn đỏ, beep dài, LCD "Unknown"
```

### Test 5 — End-to-end thật

```bash
python main.py
```

Lần lượt từng người đứng trước camera. Kiểm tra:
- ✅ Tên hiển thị đúng trên khung
- ✅ Console in `[OK] HH:MM:SS - Hoang - Diem danh OK`
- ✅ LED xanh sáng, buzzer beep, LCD hiển thị "Welcome"
- ✅ Lần 2 trong 5 phút: in `[SKIP]`, không bíp
- ✅ Người lạ: khung đỏ + LED đỏ + buzzer dài (chỉ 1 lần/3s, không spam)

---

## 🐛 Troubleshooting

| Vấn đề | Nguyên nhân & Cách fix |
|--------|------------------------|
| `Khong mo duoc webcam` | Đổi `CAM_INDEX` giữa 0 và 1 trong `config.py` |
| `Khong tim thay known_faces.pkl` | Chưa chạy `python encode_faces.py` |
| `Arduino not connected` | Sai COM port. Xem Arduino IDE → Tools → Port. Sửa `ARDUINO_PORT` trong config.py |
| `Could not open port COM7` | Arduino IDE Serial Monitor đang mở → đóng đi |
| Đèn không sáng nhưng buzzer kêu | Chân LED ngược cực. Đổi đầu LED |
| LCD bật đèn nhưng không chữ | Vặn nút chiết áp (contrast) phía sau module I2C |
| Hay bị `Unknown` | Tăng `RECOGNITION_THRESHOLD` lên 0.50 hoặc chụp thêm ảnh dataset |
| Hay nhầm người này với người khác | Giảm `RECOGNITION_THRESHOLD` xuống 0.40 |
| Dashboard không cập nhật | Bấm "Refresh ngay" trong sidebar, hoặc bật "Tự refresh" |
| FPS thấp (< 5 fps) | Tăng `RECOGNIZE_EVERY_N_FRAMES` lên 5 hoặc 7 |

---

## 🧭 Kiến trúc hệ thống

```
┌────────────────────────────────────────────────────────────────┐
│                          main.py                                │
│                                                                 │
│  ┌─────────────┐    ┌──────────┐    ┌──────────────────────┐   │
│  │  Webcam     │───>│ Slot 1   │───>│   Slot 2: db.py      │   │
│  │  (OpenCV)   │    │ recognize│    │   mark_attendance()  │   │
│  └─────────────┘    │  _frame()│    └──────────┬───────────┘   │
│                     └────┬─────┘               │                │
│                          │                     ↓                │
│                          │              ┌──────────────┐        │
│                          │              │ attendance.db│        │
│                          │              └──────┬───────┘        │
│                          ↓                     │                │
│                  ┌───────────────┐             │                │
│                  │ Slot 4: hw.py │             │                │
│                  │ signal_*()    │             │                │
│                  └───────┬───────┘             │                │
└──────────────────────────┼─────────────────────┼────────────────┘
                           │                     │
                           ↓                     ↓
                  ┌────────────────┐    ┌────────────────────┐
                  │ Arduino Uno    │    │  Slot 3 dashboard  │
                  │ (LED/Buzz/LCD) │    │  (Streamlit:8501)  │
                  └────────────────┘    └────────────────────┘
```

---

## 👥 Phân công

| Slot | Người phụ trách | Module |
|------|----------------|--------|
| 1 — AI Core | (Slot 1) | `recognize.py`, `encode_faces.py`, `capture_images.py` |
| 2 — Backend | (Slot 2) | `db.py`, `app.py`, `register_team.py`, `test_api.py` |
| 3 — Dashboard | (Slot 3) | `dashboard.py` |
| 4 — Hardware | (Slot 4) | `hardware.py`, `arduino/slot4_system.ino` |
| 5 — Integration | (Slot 5) | `main.py`, `run_all.py`, `test_integration.py`, README |

---

## 📅 Thành viên Nhóm 31

| STT | Họ và tên | MSSV |
|-----|-----------|------|
| 1 | Nguyễn Thế Hoàng | 2352354 |
| 2 | Trần Bảo Phúc Long | 2352703 |
| 3 | Đinh Hoàng Quân | 2352986 |
| 4 | Đỗ Tài Thành | 2353096 |

# Slot 2 - Backend & Database

**Hệ thống Điểm danh Nhận diện Khuôn mặt** | Nhóm 31 | HK252
Phụ trách: **Nguyễn Thế Hoàng (2352354)**

---

## 1. File trong slot này

| File | Vai trò |
|------|---------|
| `db.py` | Module SQLite cốt lõi. Slot 1 và Slot 3 đều `import` từ đây. |
| `app.py` | Flask REST API. Wrap `db.py` thành HTTP endpoints cho Slot 4 và external clients. |
| `recognize_with_attendance.py` | File tích hợp Slot 1 + Slot 2. Chạy file này khi demo. |
| `register_team.py` | Script chạy 1 lần để add 4 thành viên nhóm vào bảng `students`. |
| `test_api.py` | Test tự động toàn bộ API — chạy để chứng minh API hoạt động. |
| `attendance.db` | File SQLite (tự động sinh ra khi chạy lần đầu). |
| `backend.log` | Log của Flask app (tự động sinh ra). |

---

## 2. Cài đặt

```bash
# 1. Vào thư mục code (cùng level với Slot 1)
cd <project-root>

# 2. Cài thư viện (Slot 1 đã có requirements.txt)
pip install flask requests

# 3. Khởi tạo DB + đăng ký 4 thành viên nhóm
python db.py            # tạo file attendance.db
python register_team.py # add 4 thành viên
```

---

## 3. Chạy hệ thống

### Cách A — Demo end-to-end (cách dùng khi nộp bài)

Mở **3 terminal** song song:

```bash
# Terminal 1 — Backend API (cho Slot 4 và external)
python app.py
# -> Chạy tại http://localhost:5000

# Terminal 2 — Slot 3 (Streamlit dashboard)
streamlit run dashboard.py
# -> Mở tại http://localhost:8501

# Terminal 3 — Camera + nhận diện + ghi DB
python recognize_with_attendance.py
# -> Cửa sổ webcam mở ra, ghi attendance tự động
```

### Cách B — Chỉ test API (Slot 2 độc lập)

```bash
# Terminal 1
python app.py

# Terminal 2
python test_api.py
# -> Phải pass 23/23
```

---

## 4. Schema cơ sở dữ liệu

```sql
-- Bảng students: thông tin sinh viên (đăng ký một lần)
CREATE TABLE students (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    mssv        TEXT,
    created_at  TEXT    NOT NULL
);

-- Bảng attendance: log điểm danh (mỗi lần điểm danh = 1 dòng)
CREATE TABLE attendance (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    timestamp  TEXT    NOT NULL,        -- HH:MM:SS
    date       TEXT    NOT NULL,        -- YYYY-MM-DD
    status     TEXT    DEFAULT 'success'
);

-- Index để query theo ngày nhanh hơn
CREATE INDEX idx_att_date ON attendance(date);
CREATE INDEX idx_att_name_date ON attendance(name, date);
```

---

## 5. API Reference

Server chạy tại `http://localhost:5000`. Mọi response đều là JSON.

| Method | Endpoint | Mô tả | HTTP Code |
|--------|----------|-------|-----------|
| GET  | `/` | Health check + liệt kê endpoints | 200 |
| POST | `/attendance` | Ghi điểm danh. Body: `{"name": "Hoang"}` | 200/409/400 |
| GET  | `/attendance/today` | Danh sách điểm danh hôm nay | 200 |
| GET  | `/attendance/history?limit=100` | Lịch sử (mặc định 500) | 200 |
| GET  | `/attendance/export` | Tải file CSV | 200 |
| GET  | `/stats` | Thống kê cho dashboard | 200 |
| POST | `/students` | Đăng ký sinh viên. Body: `{"name":"...","mssv":"..."}` | 200/400 |
| GET  | `/students` | Danh sách sinh viên | 200 |

### Ví dụ với curl

```bash
# Ghi điểm danh
curl -X POST http://localhost:5000/attendance \
     -H "Content-Type: application/json" \
     -d '{"name":"Hoang"}'
# -> {"success":true,"message":"Diem danh thanh cong","name":"Hoang","timestamp":"16:30:45"}

# Lấy danh sách hôm nay
curl http://localhost:5000/attendance/today

# Tải CSV
curl http://localhost:5000/attendance/export -o today.csv
```

### HTTP Status Code

- **200** — Thành công
- **400** — Input lỗi (tên rỗng, "Unknown")
- **404** — Endpoint không tồn tại
- **409** — Đã điểm danh trong 5 phút qua (cooldown)
- **500** — Lỗi server (xem `backend.log`)

---

## 6. Hướng dẫn cho từng Slot khác

### Slot 1 (AI Core) — gọi DB trực tiếp

Trong `recognize.py` của Slot 1, sau dòng có `recognize_frame(frame)`, thêm:

```python
import db   # import module Slot 2

for name, location in results:
    if name != "Unknown":
        result = db.mark_attendance(name)
        if result["success"]:
            print(f"Đã điểm danh: {name}")
```

Hoặc tốt hơn: **chạy file `recognize_with_attendance.py`** đã viết sẵn — không cần sửa file gốc của Slot 1.

### Slot 3 (Dashboard Streamlit) — đọc DB trực tiếp

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("attendance.db")
df = pd.read_sql("SELECT * FROM attendance ORDER BY date DESC, timestamp DESC", conn)
conn.close()

st.dataframe(df)
```

Hoặc gọi API qua HTTP (ưu tiên khi muốn dashboard ở máy khác):

```python
import requests
data = requests.get("http://localhost:5000/attendance/today").json()
df = pd.DataFrame(data["data"])
```

### Slot 4 (Phần cứng) — gọi API qua serial bridge

Khi Slot 1 gọi `db.mark_attendance()` thành công, Slot 4 nhận signal từ Python (xem `signal_success()` trong file phân công gốc). Slot 4 **không cần gọi API trực tiếp** — chỉ cần Python gửi byte `b'G'` hoặc `b'R'` qua serial.

---

## 7. Quy tắc nghiệp vụ

- **Cooldown 5 phút**: cùng một người, trong cùng một ngày, không được ghi điểm danh 2 lần trong vòng 5 phút (tránh ghi trùng khi đứng trước camera lâu).
- **"Unknown"** không được ghi vào DB. Logic này bảo vệ DB khỏi nhiễu.
- **Tên rỗng** bị reject ở cả 2 layer (Python function và HTTP API).
- **Logging**: mọi POST `/attendance` được ghi vào `backend.log` cùng timestamp.

---

## 8. Test

```bash
# Test module db.py độc lập (không cần Flask)
python db.py
# -> in ra kết quả test mark_attendance, get_today, get_stats

# Test toàn bộ API (cần app.py đang chạy)
python app.py        # terminal 1
python test_api.py   # terminal 2
# -> Phải pass 23/23
```

Đính kèm `test_api.py` vào báo cáo cuối kỳ làm bằng chứng API hoạt động.

---

## 9. Phần sẽ viết trong báo cáo (Chương 3 — Công nghệ sử dụng)

Theo phân công, Slot 2 + Slot 3 cùng viết Chương 3. Phần của Slot 2 sẽ giới thiệu:

- **Flask** — micro web framework, dùng cho REST API
- **SQLite** — embedded DB, không cần server riêng, lý tưởng cho đồ án nhỏ
- **Schema thiết kế** (sơ đồ ERD đơn giản: 2 bảng students + attendance)
- **Logic chống trùng** trong vòng 5 phút (tránh ghi spam khi nhận diện liên tục)
- **REST API** — trình bày 8 endpoints + ví dụ curl

---

## 10. Liên hệ

Vấn đề phần backend → Hoàng (Slot 2). Báo qua Zalo/group nhóm 31.

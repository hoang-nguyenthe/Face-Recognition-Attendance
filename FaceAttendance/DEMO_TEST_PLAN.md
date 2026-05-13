# KẾ HOẠCH KIỂM THỬ & DEMO — Nhóm 31

Tài liệu này hướng dẫn nhóm kiểm thử có hệ thống TRƯỚC và TRONG buổi demo, để không bị bất ngờ.

---

## 📋 Phần 1 — Checklist 1 ngày trước demo

### ☐ 1.1. Môi trường

- [ ] Laptop demo cài đủ thư viện: `pip install -r requirements.txt` chạy không lỗi
- [ ] `python -c "import face_recognition; print('OK')"` chạy được
- [ ] `python -c "import cv2; print(cv2.__version__)"` chạy được
- [ ] Đã copy folder dự án vào laptop demo (không phải clone GitHub lúc demo)

### ☐ 1.2. Dữ liệu

- [ ] `dataset/` có đủ folder cho 4 thành viên: Hoang, Long, Quan, Thanh
- [ ] Mỗi folder có ít nhất 20 ảnh
- [ ] `models/known_faces.pkl` đã tồn tại và không rỗng:
  ```bash
  python -c "import pickle; d=pickle.load(open('models/known_faces.pkl','rb')); print(len(d['encodings']), 'faces,', set(d['names']))"
  ```
- [ ] Database `attendance.db` đã xóa hoặc reset (demo trên DB sạch)

### ☐ 1.3. Phần cứng (Slot 4)

- [ ] Cắm Arduino vào laptop demo, kiểm tra COM port
- [ ] Cập nhật `ARDUINO_PORT` trong `config.py` đúng port
- [ ] Đã nạp `slot4_system.ino` vào Arduino (LCD hiển thị "System Ready")
- [ ] Đèn LED xanh, đỏ, buzzer, LCD đều hoạt động (test bằng `python arduino/serial_test.py`)
- [ ] Dây cáp Arduino chắc chắn, không lỏng

### ☐ 1.4. Test tự động

- [ ] `python test_integration.py` → 19/19 PASS
- [ ] `python app.py` + `python test_api.py` → 23/23 PASS
- [ ] `python recognize.py` → đứng trước camera thấy tên đúng

### ☐ 1.5. Test end-to-end

- [ ] `python main.py` chạy được, không crash
- [ ] Đứng trước camera, thấy:
  - ✅ Khung xanh + tên trên cửa sổ OpenCV
  - ✅ Console in `[OK] HH:MM:SS - <Ten> - Diem danh OK`
  - ✅ LED xanh sáng + buzzer beep
  - ✅ LCD hiển thị "Welcome / Recognized"
- [ ] Người lạ (bạn ngoài nhóm) → khung đỏ + LED đỏ + buzzer dài + LCD "Unknown"
- [ ] Mở dashboard `streamlit run dashboard.py` → thấy tên vừa điểm danh xuất hiện

### ☐ 1.6. Backup

- [ ] Quay video demo dự phòng (~2 phút, dùng OBS Studio)
- [ ] Lưu video lên: USB + Google Drive
- [ ] In bản sao file PDF report (đề phòng wifi)
- [ ] Test lại trên 1 laptop khác (đề phòng laptop chính hỏng)

---

## 🎯 Phần 2 — Kế hoạch kiểm thử CHI TIẾT (các trường hợp)

### Test Case 1: Nhận diện thành viên trong nhóm

| # | Tình huống | Hành động | Kết quả mong đợi |
|---|-----------|-----------|------------------|
| 1.1 | Hoang đứng chính diện, ánh sáng tốt | Đứng cách 50cm, nhìn thẳng camera | Khung xanh + "Hoang", LED xanh, ghi DB |
| 1.2 | Hoang điểm danh lần 2 trong 5 phút | Vẫn đứng yên hoặc đi ra rồi vào lại | Console `[SKIP]`, không bíp buzzer, không ghi DB |
| 1.3 | Long → Quan → Thanh lần lượt | Mỗi người đứng 5 giây rồi đi | Mỗi người ghi 1 dòng vào DB, LED xanh mỗi lần |
| 1.4 | 2 người cùng vào khung hình | Đứng cạnh nhau | Cả 2 đều được nhận diện và ghi DB |

### Test Case 2: Xử lý người lạ

| # | Tình huống | Hành động | Kết quả mong đợi |
|---|-----------|-----------|------------------|
| 2.1 | Bạn ngoài nhóm đứng trước camera | Đứng yên 5 giây | Khung đỏ + "Unknown", LED đỏ, buzzer dài |
| 2.2 | Người lạ đứng lâu (10 giây) | Đứng yên | LED đỏ chỉ kêu 1 lần/3 giây (throttle, không spam) |
| 2.3 | Người lạ và thành viên cùng vào | 2 người đứng cạnh | Thành viên: xanh + ghi DB. Người lạ: đỏ. |

### Test Case 3: Điều kiện ánh sáng

| # | Tình huống | Hành động | Kết quả mong đợi |
|---|-----------|-----------|------------------|
| 3.1 | Ánh sáng tốt (đèn neon văn phòng) | Đứng trước camera | Nhận diện chính xác, distance < 0.4 |
| 3.2 | Ánh sáng yếu (đèn vàng phòng nghỉ) | Đứng trước camera | Vẫn nhận diện được, có thể chậm hơn |
| 3.3 | Ngược sáng (cửa sổ phía sau) | Đứng trước cửa sổ | Có thể bị Unknown — báo trước trong report |

### Test Case 4: Phụ kiện / che mặt

| # | Tình huống | Hành động | Kết quả mong đợi |
|---|-----------|-----------|------------------|
| 4.1 | Đeo kính cận | Hoang đeo kính nếu thường ngày không đeo | Có thể vẫn nhận đúng, hoặc Unknown (báo trong report) |
| 4.2 | Đội mũ | Đội mũ lưỡi trai | Tùy độ che, có thể Unknown |
| 4.3 | Đeo khẩu trang | Che mũi-miệng | Sẽ bị Unknown (face_recognition cần thấy đủ mặt) — KHUYẾN NGHỊ TRONG REPORT |

### Test Case 5: Dashboard

| # | Tình huống | Hành động | Kết quả mong đợi |
|---|-----------|-----------|------------------|
| 5.1 | Mở dashboard khi đã có dữ liệu | `streamlit run dashboard.py` | Thấy đủ 4 metric + bảng hôm nay + lịch sử |
| 5.2 | Auto-refresh khi điểm danh mới | Bật "Tự refresh", điểm danh thêm 1 người | Dashboard cập nhật trong ≤ 5 giây |
| 5.3 | Export CSV hôm nay | Bấm nút "📄 CSV hôm nay" | File tải về có header tiếng Việt + đủ dòng |
| 5.4 | Export Excel lịch sử | Bấm nút "📊 Excel lịch sử" | File .xlsx có 2 sheet: History + Today |

### Test Case 6: Phần cứng (Slot 4)

| # | Tình huống | Hành động | Kết quả mong đợi |
|---|-----------|-----------|------------------|
| 6.1 | Arduino không cắm | Rút Arduino, chạy `python main.py` | Console in `[HW] Khong ket noi duoc...`, app vẫn chạy bình thường, in `[HW-SIM] 🟢/🔴` thay LED |
| 6.2 | Arduino bị rút giữa chừng | Rút cáp khi đang chạy | App không crash, in lỗi rồi tiếp tục chạy ở mode console |
| 6.3 | COM port sai | Sửa COM lung tung trong config | Fallback ra console, không crash |

### Test Case 7: Khả năng phục hồi

| # | Tình huống | Hành động | Kết quả mong đợi |
|---|-----------|-----------|------------------|
| 7.1 | Camera bị che giữa chừng | Lấy tay che camera | Không có khuôn mặt, không ghi gì, không crash |
| 7.2 | Nhấn Ctrl+C khi đang chạy | Bấm Ctrl+C trên terminal | App thoát gọn gàng, in tóm tắt, đóng Arduino |
| 7.3 | Database file bị xóa giữa chừng | Xóa attendance.db | Lần ghi sau tự tạo lại DB (nhờ auto-init) |

---

## 🎬 Phần 3 — Kịch bản demo (15-20 phút)

### Phần 1 (3 phút) — Giới thiệu bài toán
- Slide tổng quan: vì sao chọn đề tài, ứng dụng thực tế
- Sơ đồ kiến trúc hệ thống

### Phần 2 (5 phút) — Demo trực tiếp

```
1. Mở terminal, gõ: python run_all.py
   → Cửa sổ camera hiện ra
   → Mở browser: http://localhost:8501

2. Hoang đứng trước camera (5 giây)
   → "Khung xanh + Hoang" trên màn hình
   → LED xanh sáng, buzzer beep
   → LCD: "Welcome! Recognized"
   → Dashboard tự cập nhật, thấy "Hoang" xuất hiện

3. Long đứng trước camera
   → Tương tự, LED xanh

4. Hoang đứng lại trước camera (test cooldown)
   → Khung xanh nhưng KHÔNG bíp (đã điểm danh rồi)

5. Nhờ thầy/bạn ngoài nhóm thử
   → Khung đỏ + "Unknown"
   → LED đỏ + buzzer dài
   → Dashboard không thêm dòng nào

6. Bấm Q thoát main.py
   → Console in tóm tắt: 2 người, sớm nhất HH:MM, muộn nhất HH:MM

7. Export CSV từ dashboard, mở file Excel
   → File có đầy đủ tên, giờ, ngày
```

### Phần 3 (3 phút) — Giải thích code

- Show `main.py` — giải thích flow: webcam → recognize → DB → hardware
- Show `db.py` — giải thích cooldown 5 phút
- Show `slot4_system.ino` — giải thích G/R command

### Phần 4 (2 phút) — Phần Q&A

Câu hỏi có thể bị hỏi và câu trả lời chuẩn bị sẵn:

| Câu hỏi | Trả lời |
|---------|---------|
| "Vì sao chọn threshold 0.45?" | Cân bằng giữa false-positive và false-negative. Test với 30 ảnh/người cho ra distance trung bình ~0.35, threshold 0.45 cho safety margin. |
| "Nếu 2 người giống nhau?" | Face encoding dlib 128-dim, ngay cả anh em sinh đôi cũng khác encoding. Trừ khi giả mạo bằng ảnh in. |
| "Có thể giả mạo bằng ảnh in?" | Có thể. Limitation chưa làm liveness detection. Trong "hướng phát triển" có nêu: blink detection / face depth. |
| "Bao nhiêu FPS?" | Tối ưu bằng cách recognize mỗi 3 frame → ~10 fps trên CPU laptop thông thường. |
| "Database scale được không?" | SQLite chịu được ~hàng nghìn record/ngày. Production nên dùng PostgreSQL. |
| "Vì sao tách Flask API và Streamlit?" | Đúng kiến trúc client-server: API cho phép mở rộng (mobile app, IoT...) còn dashboard chỉ là 1 client. |

---

## 🚨 Phần 4 — Phương án xử lý sự cố

### Plan A: Mọi thứ chạy bình thường
→ Theo kịch bản ở Phần 3.

### Plan B: Camera laptop hỏng / mở không lên
→ Đổi `CAM_INDEX` trong config.py. Nếu vẫn không được, dùng webcam USB rời (mang theo dự phòng).

### Plan C: Arduino không kết nối
→ App tự fallback ra console mode (đã test). Demo vẫn chạy đầy đủ, chỉ thiếu LED/buzzer thực tế.
Giải thích với thầy: "Hardware có cơ chế graceful fallback, đây là design choice."

### Plan D: Wifi/internet sự cố
→ Hệ thống chạy 100% local, KHÔNG cần internet. Cứ chạy bình thường.

### Plan E: Laptop chính sự cố nặng
→ Mở laptop dự phòng, đã cài sẵn môi trường. Dataset và models đã copy sẵn.

### Plan F: Toàn bộ thiết bị sự cố
→ Mở video demo backup đã quay sẵn. Giải thích "do điều kiện kỹ thuật".

---

## 📊 Phần 5 — Số liệu cho report

Sau khi test, ghi lại các số liệu thực tế vào report Chương 6 (Kết quả thực nghiệm):

| Chỉ tiêu | Kết quả đo được | Ghi chú |
|----------|----------------|---------|
| Độ chính xác (ánh sáng tốt) | _____ % | Test với N lần × 4 người |
| Độ chính xác (ánh sáng yếu) | _____ % | |
| Tỷ lệ false-positive (Unknown bị nhận thành member) | _____ % | Test với 5 người lạ × 5 lần |
| Thời gian nhận diện trung bình | _____ ms | Đo bằng `time.time()` quanh `recognize_frame` |
| FPS trung bình | _____ | Đọc từ overlay góc trên main.py |
| Số face encoding/người | 30 | Mặc định |
| Threshold tối ưu | 0.45 | Sau khi test thử |
| Cooldown | 5 phút | Theo phân công gốc |

---

**Phiên bản:** v1.0 | Cập nhật: trước demo

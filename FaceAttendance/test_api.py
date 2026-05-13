"""
test_api.py - Test tu dong tat ca endpoint cua app.py

YEU CAU:
    - app.py phai dang chay (mo terminal khac chay 'python app.py' truoc)
    - Da cai requests: pip install requests

CHAY:
    python test_api.py

KET QUA:
    In ra ket qua test cua tung endpoint. Dung de chung minh API hoat dong
    trong report cua mon hoc.
"""

import requests
import time
import sys
import os
import config

BASE_URL = config.BACKEND_URL

# Dem so test pass / fail
passed = 0
failed = 0


def check(condition, name):
    """Test helper - in ket qua mau."""
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name}")


def section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def test_health():
    section("1. Health check (GET /)")
    r = requests.get(f"{BASE_URL}/")
    print(f"  Status: {r.status_code}")
    check(r.status_code == 200, "Status code 200")
    data = r.json()
    check(data.get("status") == "ok", "Field status = 'ok'")
    check("endpoints" in data, "Co liet ke endpoints")


def test_post_attendance():
    section("2. POST /attendance")

    # Test 1: Diem danh hop le
    r = requests.post(f"{BASE_URL}/attendance", json={"name": "TestUser1"})
    print(f"  Lan 1 - Status: {r.status_code}, Body: {r.json()}")
    check(r.status_code == 200, "Diem danh moi -> 200")
    check(r.json().get("success") is True, "success = True")

    # Test 2: Cooldown - diem danh lai trong 5 phut
    r = requests.post(f"{BASE_URL}/attendance", json={"name": "TestUser1"})
    print(f"  Lan 2 - Status: {r.status_code}, Body: {r.json()}")
    check(r.status_code == 409, "Cooldown -> 409")
    check(r.json().get("success") is False, "success = False")

    # Test 3: Unknown
    r = requests.post(f"{BASE_URL}/attendance", json={"name": "Unknown"})
    print(f"  Unknown - Status: {r.status_code}")
    check(r.status_code == 400, "Unknown -> 400")

    # Test 4: Ten rong
    r = requests.post(f"{BASE_URL}/attendance", json={"name": ""})
    print(f"  Ten rong - Status: {r.status_code}")
    check(r.status_code == 400, "Ten rong -> 400")


def test_get_today():
    section("3. GET /attendance/today")
    r = requests.get(f"{BASE_URL}/attendance/today")
    print(f"  Status: {r.status_code}")
    data = r.json()
    print(f"  So dong: {len(data.get('data', []))}")
    check(r.status_code == 200, "Status 200")
    check(isinstance(data.get("data"), list), "data la list")
    check(len(data["data"]) > 0, "Co it nhat 1 ban ghi (TestUser1 vua tao)")


def test_get_history():
    section("4. GET /attendance/history")
    r = requests.get(f"{BASE_URL}/attendance/history?limit=10")
    print(f"  Status: {r.status_code}")
    check(r.status_code == 200, "Status 200")
    check(isinstance(r.json().get("data"), list), "data la list")


def test_export_csv():
    section("5. GET /attendance/export")
    r = requests.get(f"{BASE_URL}/attendance/export")
    print(f"  Status: {r.status_code}")
    print(f"  Content-Type: {r.headers.get('Content-Type')}")
    print(f"  Kich thuoc: {len(r.content)} bytes")
    check(r.status_code == 200, "Status 200")
    check("text/csv" in r.headers.get("Content-Type", ""), "Content-Type la CSV")
    check(b"ID,Ten,Thoi gian" in r.content, "Co header CSV")


def test_stats():
    section("6. GET /stats")
    r = requests.get(f"{BASE_URL}/stats")
    print(f"  Status: {r.status_code}")
    print(f"  Body: {r.json()}")
    check(r.status_code == 200, "Status 200")
    data = r.json().get("data", {})
    check("today_count" in data, "Co field today_count")
    check("earliest_today" in data, "Co field earliest_today")


def test_students():
    section("7. POST /students + GET /students")

    # Them sinh vien
    r = requests.post(f"{BASE_URL}/students",
                       json={"name": "Test Sinh Vien", "mssv": "9999999"})
    print(f"  POST - Status: {r.status_code}, Body: {r.json()}")

    # Them lai (phai bi reject vi UNIQUE)
    r2 = requests.post(f"{BASE_URL}/students",
                        json={"name": "Test Sinh Vien", "mssv": "9999999"})
    print(f"  POST lan 2 - Status: {r2.status_code}")
    check(r2.status_code == 400, "Trung ten -> 400")

    # Lay danh sach
    r3 = requests.get(f"{BASE_URL}/students")
    print(f"  GET - Status: {r3.status_code}, So sinh vien: {len(r3.json()['data'])}")
    check(r3.status_code == 200, "GET 200")


def test_404():
    section("8. Endpoint khong ton tai")
    r = requests.get(f"{BASE_URL}/khong-ton-tai")
    print(f"  Status: {r.status_code}")
    check(r.status_code == 404, "Status 404")


# ============== MAIN ==============
def main():
    print("=" * 60)
    print("TEST AUTOMATION - Slot 2 Backend - Nhom 31")
    print("=" * 60)
    print(f"Target: {BASE_URL}")

    # Don dep DB cu de test sach (xoa neu test_api.db ton tai)
    # Hoac luu y: test nay se ghi vao attendance.db that
    print("\nKiem tra server...")
    try:
        requests.get(f"{BASE_URL}/", timeout=2)
        print("Server OK\n")
    except requests.exceptions.RequestException:
        print("KHONG KET NOI DUOC SERVER!")
        print("Chay 'python app.py' trong terminal khac truoc khi test.")
        sys.exit(1)

    try:
        test_health()
        test_post_attendance()
        test_get_today()
        test_get_history()
        test_export_csv()
        test_stats()
        test_students()
        test_404()
    except Exception as e:
        print(f"\nLOI TRONG QUA TRINH TEST: {e}")
        sys.exit(1)

    # Tom tat
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"  TONG KET: {passed}/{total} PASS, {failed} FAIL")
    print("=" * 60)

    if failed == 0:
        print("  TAT CA TEST DEU PASS!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
test_integration.py - Kiem tra TICH HOP cac module (khong can camera/Arduino that)
=================================================================================

Test nay mo phong recognize_frame tra ve ten -> chay xuyen suot:
    db.mark_attendance -> HardwareController.signal_*

Dung de kiem chung logic tich hop TRUOC khi chay main.py.

CHAY:
    python test_integration.py
"""

import time
import os
import config


# Force hardware sang console mode de test khong can Arduino
os.environ["HARDWARE_ENABLED"] = "false"

# Doi DB sang file test rieng, khong dung lai DB that
TEST_DB = "test_integration.db"
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
os.environ["ATTENDANCE_DB"] = TEST_DB

# Reload config voi env moi
import importlib
importlib.reload(config)

import db
from hardware import HardwareController


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def assert_eq(actual, expected, label):
    ok = actual == expected
    icon = "[PASS]" if ok else "[FAIL]"
    print(f"  {icon} {label}: got {actual!r}, expected {expected!r}")
    return ok


def main():
    print("=" * 60)
    print("TEST TICH HOP - KHONG CAN CAMERA / ARDUINO THAT")
    print("=" * 60)

    passed = 0
    failed = 0

    def check(cond, label):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  [PASS] {label}")
        else:
            failed += 1
            print(f"  [FAIL] {label}")

    # === Test 1: DB init ===
    section("Test 1: DB khoi tao tu dong khi import")
    check(os.path.exists(TEST_DB), "File test_integration.db da tao")

    # === Test 2: register students ===
    section("Test 2: Dang ky thanh vien")
    r = db.register_student("Hoang", "2352354")
    check(r["success"], "Dang ky Hoang -> success")
    r = db.register_student("Hoang", "2352354")
    check(not r["success"], "Dang ky lai Hoang -> bi tu choi (UNIQUE)")
    students = db.get_students()
    check(len(students) == 1, f"Co 1 sinh vien trong DB (got {len(students)})")

    # === Test 3: mark attendance ===
    section("Test 3: Diem danh co ban")
    r = db.mark_attendance("Hoang")
    check(r["success"], "Diem danh Hoang lan 1 -> success")
    check(r["timestamp"] is not None, "Co timestamp")

    r = db.mark_attendance("Hoang")
    check(not r["success"], "Diem danh Hoang lan 2 (cooldown) -> reject")
    check("Da diem danh" in r["message"], f"Message dung: {r['message']}")

    r = db.mark_attendance("Unknown")
    check(not r["success"], "Diem danh Unknown -> reject")

    r = db.mark_attendance("")
    check(not r["success"], "Diem danh ten rong -> reject")

    r = db.mark_attendance("Long")
    check(r["success"], "Diem danh Long -> success")

    # === Test 4: Query ===
    section("Test 4: Query DB")
    today = db.get_today()
    check(len(today) == 2, f"get_today tra 2 ban ghi (got {len(today)})")
    all_rows = db.get_all()
    check(len(all_rows) == 2, f"get_all tra 2 ban ghi (got {len(all_rows)})")

    stats = db.get_stats()
    check(stats["today_count"] == 2, f"today_count = 2 (got {stats['today_count']})")
    check(stats["today_total"] == 2, f"today_total = 2 (got {stats['today_total']})")
    check(stats["earliest_today"] is not None, "earliest_today co gia tri")

    # === Test 5: Hardware fallback ===
    section("Test 5: HardwareController (mode fallback console)")
    hw = HardwareController()
    check(not hw.connected, "Khong connect Arduino (vi disabled) -> dung")

    print("\n  -- Test signal_success --")
    hw.signal_success("Hoang")
    print("\n  -- Test signal_unknown (5 lan lien tiep, phai bi throttle) --")
    for i in range(5):
        hw.signal_unknown()
        time.sleep(0.2)
    print("  (chi nen thay 1 dong [HW-SIM] RED, cac lan sau bi throttle)")

    hw.close()
    check(True, "Hardware close khong loi")

    # === Test 6: Full pipeline mo phong ===
    section("Test 6: Mo phong pipeline day du (recognize -> db -> hw)")
    hw = HardwareController()

    # Gia su recognize_frame tra ket qua nay
    fake_results_sequence = [
        [("Hoang", (0, 100, 100, 0))],     # frame 1: Hoang
        [("Hoang", (0, 100, 100, 0))],     # frame 2: Hoang (cooldown)
        [("Unknown", (0, 100, 100, 0))],   # frame 3: Unknown
        [("Long", (0, 100, 100, 0))],      # frame 4: Long (cooldown vi da diem danh o test 3)
        [("Quan", (0, 100, 100, 0))],      # frame 5: Quan moi
    ]

    last_status = {}
    success_count = 0
    for i, results in enumerate(fake_results_sequence, 1):
        print(f"\n  Frame {i}: {results}")
        for name, loc in results:
            if name == "Unknown":
                hw.signal_unknown()
                continue
            r = db.mark_attendance(name)
            status = "success" if r["success"] else "cooldown"
            prev = last_status.get(name)
            if prev != status:
                if r["success"]:
                    print(f"    -> OK: {name}")
                    hw.signal_success(name)
                    success_count += 1
                else:
                    print(f"    -> SKIP: {name} ({r['message']})")
                last_status[name] = status

    check(success_count == 1, f"Chi 1 diem danh moi (Quan), got {success_count}")
    hw.close()

    # === Tom tat ===
    section("KET QUA")
    total = passed + failed
    print(f"  Pass: {passed}/{total}")
    print(f"  Fail: {failed}/{total}")
    if failed == 0:
        print("\n  TAT CA TEST DEU PASS. He thong tich hop OK.")
    else:
        print(f"\n  CO {failed} TEST FAIL. Kiem tra lai.")

    # Don dep
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
        print(f"\n  Da xoa {TEST_DB}")


if __name__ == "__main__":
    main()

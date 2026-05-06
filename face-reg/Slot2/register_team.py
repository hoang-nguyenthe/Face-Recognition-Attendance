"""
register_team.py
================
Script chay 1 lan de them 4 thanh vien Nhom 31 vao bang students.

CHAY:
    python register_team.py

LUU Y:
    Neu sinh vien da ton tai thi se in 'da ton tai' va bo qua.
    Khong xoa du lieu cu.
"""

import db

TEAM = [
    ("Nguyen The Hoang", "2352354"),
    ("Tran Bao Phuc Long", "2352703"),
    ("Dinh Hoang Quan", "2352986"),
    ("Do Tai Thanh", "2353096"),
]


def main():
    print("=" * 60)
    print("DANG KY THANH VIEN NHOM 31")
    print("=" * 60)
    for name, mssv in TEAM:
        result = db.register_student(name, mssv)
        marker = "OK" if result["success"] else "SKIP"
        print(f"  [{marker}] {name} ({mssv}) - {result['message']}")

    print("\nDanh sach hien tai trong DB:")
    for s in db.get_students():
        print(f"  - {s['name']} ({s['mssv']})")


if __name__ == "__main__":
    main()

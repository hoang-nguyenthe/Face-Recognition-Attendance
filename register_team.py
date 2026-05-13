"""
register_team.py - Dang ky 4 thanh vien Nhom 31 vao DB
=======================================================
Chay 1 lan duy nhat sau khi co attendance.db.

CHAY:
    python register_team.py

LUU Y:
    - Ten o day PHAI khop voi ten folder trong dataset/
    - Vi du: neu folder la "Hoang" thi o day cung phai la "Hoang"
    - Neu da ton tai thi se skip, khong xoa du lieu cu
"""

import db

# Sua ten cho khop voi ten folder dataset/<ten>/
# Khuyen nghi dung ten ngan khong dau: "Hoang", "Long", "Quan", "Thanh"
TEAM = [
    ("Hoang", "2352354"),
    ("Long", "2352703"),
    ("Quan", "2352986"),
    ("Thanh", "2353096"),
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

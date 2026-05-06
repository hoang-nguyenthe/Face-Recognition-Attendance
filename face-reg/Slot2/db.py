"""
db.py - Module quan ly co so du lieu cho he thong diem danh
Slot 2 - Backend & Database
Nhom 31 - HK252

Schema:
    students(id, name, mssv, created_at)
    attendance(id, name, timestamp, date, status)

Cac ham public:
    init_db()                    -> Khoi tao DB + tables
    mark_attendance(name)        -> Ghi diem danh, tra dict ket qua
    get_today()                  -> Lay diem danh hom nay
    get_all()                    -> Lay toan bo lich su
    get_stats()                  -> Thong ke (tong, som nhat, muon nhat)
    register_student(name, mssv) -> Them sinh vien moi
    get_students()               -> Danh sach sinh vien
"""

import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import contextmanager

# ============== CAU HINH ==============
DB_PATH = os.environ.get("ATTENDANCE_DB", "attendance.db")
COOLDOWN_MINUTES = 5  # Khong cho diem danh lai trong 5 phut (theo phan cong goc)


# ============== HELPER ==============
@contextmanager
def get_conn():
    """Context manager dam bao luon dong connection. Row factory de truy xuat theo ten cot."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _now():
    """Tra ve datetime hien tai. Tach ra de de mock khi test."""
    return datetime.now()


# ============== INIT ==============
def init_db():
    """Tao bang neu chua co. Goi mot lan khi start app."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                mssv TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                date TEXT NOT NULL,
                status TEXT DEFAULT 'success'
            )
        """)
        # Index de query nhanh hon
        conn.execute("CREATE INDEX IF NOT EXISTS idx_att_date ON attendance(date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_att_name_date ON attendance(name, date)")


# ============== ATTENDANCE LOGIC ==============
def mark_attendance(name):
    """
    Ghi diem danh cho 'name'. Khong ghi neu vua moi diem danh trong COOLDOWN_MINUTES.

    Args:
        name: ten nguoi (tu Slot 1 - recognize.py tra ve)

    Returns:
        dict: {
            "success": bool,
            "message": str,
            "name": str,
            "timestamp": str hoac None
        }

    Quy tac:
        - name = "Unknown" -> tu choi
        - name vua diem danh trong 5 phut -> tra success=False
        - Truong hop khac -> ghi DB, tra success=True
    """
    if not name or not name.strip():
        return {"success": False, "message": "Ten rong", "name": name, "timestamp": None}

    name = name.strip()

    if name.lower() == "unknown":
        return {"success": False, "message": "Khong nhan dien duoc", "name": name, "timestamp": None}

    now = _now()
    today_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%H:%M:%S")
    cutoff = (now - timedelta(minutes=COOLDOWN_MINUTES)).strftime("%H:%M:%S")

    with get_conn() as conn:
        # Kiem tra diem danh gan day
        recent = conn.execute(
            """SELECT timestamp FROM attendance
               WHERE name = ? AND date = ? AND timestamp >= ?
               ORDER BY timestamp DESC LIMIT 1""",
            (name, today_str, cutoff)
        ).fetchone()

        if recent:
            return {
                "success": False,
                "message": f"Da diem danh luc {recent['timestamp']}",
                "name": name,
                "timestamp": recent["timestamp"]
            }

        # Ghi moi
        conn.execute(
            "INSERT INTO attendance (name, timestamp, date, status) VALUES (?, ?, ?, 'success')",
            (name, timestamp_str, today_str)
        )

    return {
        "success": True,
        "message": "Diem danh thanh cong",
        "name": name,
        "timestamp": timestamp_str
    }


# ============== QUERY ==============
def get_today():
    """
    Tra ve danh sach diem danh hom nay, sap xep theo timestamp giam dan.

    Returns:
        list of dict: [{"id":..., "name":..., "timestamp":..., "date":...}, ...]
    """
    today_str = _now().strftime("%Y-%m-%d")
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT id, name, timestamp, date, status FROM attendance
               WHERE date = ? AND status = 'success'
               ORDER BY timestamp DESC""",
            (today_str,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_all(limit=500):
    """
    Tra ve toan bo lich su, moi nhat truoc, gioi han 500 dong.

    Args:
        limit: so dong toi da tra ve

    Returns:
        list of dict
    """
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT id, name, timestamp, date, status FROM attendance
               WHERE status = 'success'
               ORDER BY date DESC, timestamp DESC LIMIT ?""",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_stats():
    """
    Thong ke cho dashboard (Slot 3 dung).

    Returns:
        dict: {
            "today_count": so nguoi diem danh hom nay (unique),
            "today_total": tong luot diem danh hom nay,
            "all_time_total": tong luot moi thoi gian,
            "earliest_today": gio som nhat hom nay,
            "latest_today": gio muon nhat hom nay,
            "unique_students": so sinh vien duy nhat
        }
    """
    today_str = _now().strftime("%Y-%m-%d")
    with get_conn() as conn:
        today = conn.execute(
            """SELECT
                   COUNT(DISTINCT name) AS unique_count,
                   COUNT(*) AS total_count,
                   MIN(timestamp) AS earliest,
                   MAX(timestamp) AS latest
               FROM attendance WHERE date = ? AND status = 'success'""",
            (today_str,)
        ).fetchone()

        all_total = conn.execute(
            "SELECT COUNT(*) AS c FROM attendance WHERE status = 'success'"
        ).fetchone()["c"]

        unique_students = conn.execute(
            "SELECT COUNT(DISTINCT name) AS c FROM attendance"
        ).fetchone()["c"]

    return {
        "today_count": today["unique_count"] or 0,
        "today_total": today["total_count"] or 0,
        "all_time_total": all_total or 0,
        "earliest_today": today["earliest"],
        "latest_today": today["latest"],
        "unique_students": unique_students or 0
    }


# ============== STUDENTS ==============
def register_student(name, mssv=""):
    """
    Them sinh vien moi vao bang students.

    Returns:
        dict: {"success": bool, "message": str}
    """
    if not name or not name.strip():
        return {"success": False, "message": "Ten rong"}

    name = name.strip()
    mssv = (mssv or "").strip()
    created_at = _now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO students (name, mssv, created_at) VALUES (?, ?, ?)",
                (name, mssv, created_at)
            )
        return {"success": True, "message": f"Da them sinh vien {name}"}
    except sqlite3.IntegrityError:
        return {"success": False, "message": f"Sinh vien {name} da ton tai"}


def get_students():
    """Lay danh sach sinh vien."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, mssv, created_at FROM students ORDER BY name"
        ).fetchall()
    return [dict(r) for r in rows]


# ============== AUTO-INIT ==============
# Khi import module nay lan dau, tu dong tao DB neu chua co.
# Tien cho Slot 1 va Slot 3 - khong can goi init_db() rieng.
init_db()


if __name__ == "__main__":
    # Chay 'python db.py' de test nhanh
    print(f"DB tai: {os.path.abspath(DB_PATH)}")

    print("\nTest mark_attendance:")
    print(mark_attendance("Hoang"))
    print(mark_attendance("Hoang"))      # Phai bi block do cooldown
    print(mark_attendance("Long"))
    print(mark_attendance("Unknown"))    # Phai bi tu choi
    print(mark_attendance(""))           # Ten rong

    print("\nHom nay:")
    for r in get_today():
        print(f"  {r['timestamp']} - {r['name']}")

    print("\nStats:")
    print(get_stats())

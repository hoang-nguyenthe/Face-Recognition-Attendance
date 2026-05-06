"""
app.py - Flask REST API cho he thong diem danh
Slot 2 - Backend & Database
Nhom 31 - HK252

Chay:
    python app.py
    -> Server tai http://localhost:5000

Endpoints:
    GET  /                       -> Health check + danh sach endpoints
    POST /attendance             -> Diem danh, body: {"name": "Hoang"}
    GET  /attendance/today       -> Danh sach hom nay
    GET  /attendance/history     -> Lich su (query: ?limit=100)
    GET  /attendance/export      -> Tai CSV file
    GET  /stats                  -> Thong ke cho dashboard
    POST /students               -> Them sinh vien, body: {"name":"...", "mssv":"..."}
    GET  /students               -> Danh sach sinh vien
"""

from flask import Flask, request, jsonify, Response
import csv
import io
import logging
import db as database  # Tranh nham voi flask 'db' cua mot so framework

# ============== APP ==============
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False  # Tra ve JSON co dau tieng Viet


# ============== CORS (cho phep Streamlit goi API) ==============
@app.after_request
def add_cors_headers(response):
    """Bat CORS cho moi response - de Slot 3 (Streamlit) goi API qua trinh duyet."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# ============== LOGGING ==============
logging.basicConfig(
    filename="backend.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ============== ROUTES ==============
@app.route("/", methods=["GET"])
def index():
    """Health check + liet ke cac endpoints co san."""
    return jsonify({
        "status": "ok",
        "service": "Face Recognition Attendance API",
        "team": "Nhom 31 - HK252",
        "endpoints": {
            "POST /attendance": "Diem danh - body: {\"name\": \"Hoang\"}",
            "GET /attendance/today": "Danh sach diem danh hom nay",
            "GET /attendance/history": "Lich su (query ?limit=100)",
            "GET /attendance/export": "Tai file CSV",
            "GET /stats": "Thong ke",
            "POST /students": "Them sinh vien - body: {\"name\":\"...\", \"mssv\":\"...\"}",
            "GET /students": "Danh sach sinh vien"
        }
    })


@app.route("/attendance", methods=["POST"])
def post_attendance():
    """
    Endpoint chinh - Slot 1 hoac Slot 4 goi day de ghi diem danh.

    Body JSON: {"name": "Ten nguoi"}
    Returns: dict tu mark_attendance()

    HTTP code:
        200: ghi thanh cong
        409: bi cooldown (da diem danh trong 5 phut)
        400: input loi (ten rong, "Unknown")
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")

    result = database.mark_attendance(name)

    # Xac dinh HTTP status code
    if result["success"]:
        status = 200
        logging.info(f"Marked: {result['name']} at {result['timestamp']}")
    elif "Da diem danh" in result["message"]:
        status = 409  # Conflict - da ton tai
        logging.info(f"Cooldown: {result['name']}")
    else:
        status = 400  # Bad Request - ten rong / Unknown
        logging.warning(f"Reject: name='{name}', reason={result['message']}")

    return jsonify(result), status


@app.route("/attendance/today", methods=["GET"])
def get_today():
    """Slot 3 (dashboard) goi de hien thi diem danh hom nay."""
    return jsonify({
        "success": True,
        "data": database.get_today()
    })


@app.route("/attendance/history", methods=["GET"])
def get_history():
    """Slot 3 goi de hien thi lich su. Mac dinh 500 dong."""
    try:
        limit = int(request.args.get("limit", 500))
        limit = max(1, min(limit, 5000))  # Gioi han an toan
    except ValueError:
        limit = 500

    return jsonify({
        "success": True,
        "data": database.get_all(limit=limit)
    })


@app.route("/attendance/export", methods=["GET"])
def export_csv():
    """
    Tra ve file CSV cua toan bo lich su. Slot 3 va thay co the tai truc tiep.
    """
    rows = database.get_all(limit=5000)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Ten", "Thoi gian", "Ngay", "Trang thai"])
    for r in rows:
        writer.writerow([r["id"], r["name"], r["timestamp"], r["date"], r["status"]])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=attendance_export.csv"
        }
    )


@app.route("/stats", methods=["GET"])
def stats():
    """Thong ke - Slot 3 dung de hien metric."""
    return jsonify({
        "success": True,
        "data": database.get_stats()
    })


@app.route("/students", methods=["POST"])
def post_student():
    """Dang ky sinh vien. Body: {\"name\":\"Hoang\", \"mssv\":\"2352354\"}"""
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")
    mssv = data.get("mssv", "")

    result = database.register_student(name, mssv)
    status = 200 if result["success"] else 400
    return jsonify(result), status


@app.route("/students", methods=["GET"])
def get_students_route():
    """Lay danh sach sinh vien - Slot 1 co the dung de validate."""
    return jsonify({
        "success": True,
        "data": database.get_students()
    })


# ============== ERROR HANDLERS ==============
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "message": "Endpoint khong ton tai"}), 404


@app.errorhandler(500)
def server_error(e):
    logging.error(f"Server error: {e}")
    return jsonify({"success": False, "message": "Loi server"}), 500


# ============== MAIN ==============
if __name__ == "__main__":
    print("=" * 60)
    print("Backend He thong Diem danh - Slot 2 - Nhom 31")
    print("=" * 60)
    print("Server chay tai: http://localhost:5000")
    print("Test nhanh: curl http://localhost:5000/")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)

"""
dashboard.py - Web Dashboard (Slot 3)
=====================================

Hien thi danh sach diem danh + export CSV/Excel.
Tu refresh moi vai giay -> trong demo thay co the thay du lieu cap nhat live.

CHAY:
    streamlit run dashboard.py
    -> Mo trinh duyet tai http://localhost:8501

LUU Y:
    - Dashboard nay doc TRUC TIEP tu SQLite (attendance.db cung folder)
    - Khong can chay backend app.py truoc - tien khi demo
    - Neu muon dung qua API (kien truc dung hon): bat USE_API=True
"""

import streamlit as st
import pandas as pd
import sqlite3
import requests
from datetime import date
import io
import time
import config


# ============== CAU HINH ==============
# True = goi REST API qua Flask (dung kien truc client-server)
# False = doc truc tiep tu SQLite (don gian, ko can chay backend)
USE_API = False


# ============== DATA LOADING ==============
@st.cache_data(ttl=config.DASHBOARD_AUTO_REFRESH_SEC)
def load_from_db():
    """Doc truc tiep tu SQLite. Cache de tranh query qua nhanh."""
    conn = sqlite3.connect(config.DB_PATH)
    today_str = date.today().strftime("%Y-%m-%d")
    df_today = pd.read_sql(
        "SELECT name, timestamp FROM attendance "
        "WHERE date = ? AND status = 'success' "
        "ORDER BY timestamp DESC",
        conn, params=(today_str,)
    )
    df_all = pd.read_sql(
        "SELECT id, name, timestamp, date, status FROM attendance "
        "WHERE status = 'success' "
        "ORDER BY date DESC, timestamp DESC LIMIT 1000",
        conn
    )
    conn.close()
    return df_today, df_all


@st.cache_data(ttl=config.DASHBOARD_AUTO_REFRESH_SEC)
def load_from_api():
    """Goi API Slot 2. Yeu cau app.py dang chay."""
    try:
        r1 = requests.get(f"{config.BACKEND_URL}/attendance/today", timeout=2)
        r2 = requests.get(f"{config.BACKEND_URL}/attendance/history", timeout=2)
        df_today = pd.DataFrame(r1.json().get("data", []))
        df_all = pd.DataFrame(r2.json().get("data", []))
        # Lay 2 cot quan trong cho today
        if not df_today.empty:
            df_today = df_today[["name", "timestamp"]]
        return df_today, df_all
    except Exception as e:
        st.error(f"Khong ket noi duoc backend tai {config.BACKEND_URL}: {e}")
        st.info("Goi y: chay 'python app.py' o terminal khac, hoac dat USE_API=False.")
        return pd.DataFrame(columns=["name", "timestamp"]), pd.DataFrame()


def load_data():
    if USE_API:
        return load_from_api()
    return load_from_db()


# ============== UI ==============
st.set_page_config(
    page_title="Hệ thống Điểm danh - Nhóm 31",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Header
st.title("📷 Hệ thống Điểm danh - Nhóm 31")
st.caption(
    f"Face Recognition Attendance System | HK252 | "
    f"Nguồn dữ liệu: {'REST API (Slot 2)' if USE_API else 'SQLite trực tiếp'}"
)

# Sidebar - control
with st.sidebar:
    st.header("⚙️ Điều khiển")
    auto_refresh = st.checkbox("Tự refresh", value=True,
                                help=f"Cứ {config.DASHBOARD_AUTO_REFRESH_SEC}s tải lại 1 lần")
    if st.button("🔄 Refresh ngay"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.subheader("ℹ️ Hướng dẫn demo")
    st.markdown(
        "1. Chạy `python main.py` ở terminal khác\n"
        "2. Đứng trước camera\n"
        "3. Xem dashboard cập nhật live\n"
        "4. Tải CSV/Excel khi cần"
    )

# Load
df_today, df_all = load_data()

# Metrics
st.markdown("### 📊 Chỉ số")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Có mặt hôm nay", len(df_today["name"].unique()) if not df_today.empty else 0)
col2.metric("Lượt điểm danh hôm nay", len(df_today))
col3.metric("Tổng lịch sử", len(df_all))

if not df_today.empty:
    earliest = df_today["timestamp"].min()
    latest = df_today["timestamp"].max()
    col4.metric("Sớm nhất / Muộn nhất", f"{earliest}", delta=f"→ {latest}", delta_color="off")
else:
    col4.metric("Sớm nhất / Muộn nhất", "—")

st.markdown("---")

# Today table
left, right = st.columns([3, 2])

with left:
    st.subheader(f"✅ Điểm danh hôm nay ({date.today().strftime('%d/%m/%Y')})")
    if df_today.empty:
        st.info("Chưa có ai điểm danh hôm nay. Chạy `python main.py` và đứng trước camera.")
    else:
        st.dataframe(df_today, use_container_width=True, hide_index=True)

with right:
    st.subheader("📈 Tần suất")
    if not df_today.empty:
        counts = df_today["name"].value_counts().reset_index()
        counts.columns = ["Tên", "Số lần"]
        st.dataframe(counts, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu.")

st.markdown("---")
st.subheader("📜 Lịch sử toàn bộ")
if df_all.empty:
    st.info("Chưa có dữ liệu lịch sử.")
else:
    st.dataframe(df_all, use_container_width=True, hide_index=True)

# Export
st.markdown("---")
st.subheader("📥 Xuất dữ liệu")
exp1, exp2, exp3 = st.columns(3)

with exp1:
    csv_today = df_today.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📄 CSV hôm nay",
        csv_today,
        f"diemdanh_{date.today().strftime('%Y%m%d')}.csv",
        "text/csv",
        use_container_width=True,
        disabled=df_today.empty
    )

with exp2:
    if not df_all.empty:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_all.to_excel(writer, index=False, sheet_name="History")
            if not df_today.empty:
                df_today.to_excel(writer, index=False, sheet_name="Today")
        st.download_button(
            "📊 Excel lịch sử",
            buf.getvalue(),
            f"lichsu_{date.today().strftime('%Y%m%d')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.button("📊 Excel lịch sử", disabled=True, use_container_width=True)

with exp3:
    csv_all = df_all.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📄 CSV lịch sử",
        csv_all,
        f"lichsu_{date.today().strftime('%Y%m%d')}.csv",
        "text/csv",
        use_container_width=True,
        disabled=df_all.empty
    )

# Auto-refresh
if auto_refresh:
    time.sleep(config.DASHBOARD_AUTO_REFRESH_SEC)
    st.rerun()

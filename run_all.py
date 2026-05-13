"""
run_all.py - Chay main.py va dashboard.py cung luc
==================================================

Tien khi demo: chi can 1 lenh la mo ca camera lan dashboard.

CHAY:
    python run_all.py

Se mo:
    - Cua so OpenCV: nhan dien khuon mat
    - Browser tab tai http://localhost:8501: dashboard

THOAT:
    - Ctrl+C tren terminal nay -> dung ca 2
    - Hoac nhan Q tren cua so OpenCV
"""

import subprocess
import sys
import time
import os
import signal

# Doi sang folder cua script (de tim dung file)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

procs = []


def start(name, cmd):
    print(f"[Launcher] Start {name}: {' '.join(cmd)}")
    # creationflags chi tren Windows
    if sys.platform.startswith("win"):
        p = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        p = subprocess.Popen(cmd)
    procs.append((name, p))
    return p


def cleanup():
    print("\n[Launcher] Dang dong tat ca process...")
    for name, p in procs:
        if p.poll() is None:
            print(f"  Stop {name} (PID {p.pid})")
            try:
                p.terminate()
            except Exception:
                pass
    time.sleep(1)
    for name, p in procs:
        if p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass
    print("[Launcher] Da dong.")


def main():
    print("=" * 60)
    print("NHOM 31 - LAUNCHER")
    print("=" * 60)

    # 1. Start dashboard
    start("dashboard", [
        sys.executable, "-m", "streamlit", "run", "dashboard.py",
        "--server.headless", "true",
        "--server.runOnSave", "false"
    ])
    time.sleep(3)  # Cho dashboard khoi dong xong
    print("[Launcher] Dashboard: http://localhost:8501")
    print("[Launcher] Mo trinh duyet thu cong de xem dashboard.")
    print()

    # 2. Start main camera loop
    start("main", [sys.executable, "main.py"])

    print()
    print("=" * 60)
    print("System dang chay. Nhan Ctrl+C de dung.")
    print("=" * 60)

    try:
        # Cho cho process main ket thuc (user nhan Q)
        for name, p in procs:
            if name == "main":
                p.wait()
                break
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[Launcher] Loi: {e}")
        cleanup()
        raise

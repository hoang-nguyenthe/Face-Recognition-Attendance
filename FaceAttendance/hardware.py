"""
hardware.py - Module dieu khien phan cung Arduino (Slot 4)
==========================================================

Cung cap class HardwareController dong vai tro adapter:
    - Neu co Arduino -> gui tin hieu serial that
    - Neu khong co Arduino -> in ra console (mode gia lap)

Cach dung:
    from hardware import HardwareController
    hw = HardwareController()
    hw.signal_success("Hoang")     # LED xanh + buzzer ngan + LCD "Welcome"
    hw.signal_unknown()            # LED do + buzzer dai + LCD "Unknown"
    hw.close()

Cac sua doi so voi code Slot 4 goc:
    - Dong goi thanh class de de mock khi test
    - Throttle tin hieu R (Unknown) de tranh spam buzzer
    - Auto-fallback ra console mode neu khong ket noi duoc Arduino
    - Khong crash chuong trinh chinh neu Arduino bi rut day giua chung
"""

import time
import config

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class HardwareController:
    """
    Bao boc Arduino serial communication.
    Tu dong fallback ra console mode neu khong co Arduino.
    """

    def __init__(self):
        self.arduino = None
        self.connected = False
        self._last_unknown_signal_time = 0.0
        self._last_signal_cmd = None  # Tranh gui lien tuc cung 1 lenh

        # Quyet dinh co thu ket noi khong
        if config.HARDWARE_ENABLED == "false":
            print("[HW] Hardware DISABLED (HARDWARE_ENABLED=false). Chay console mode.")
            return

        if not SERIAL_AVAILABLE:
            print("[HW] Thu vien pyserial chua duoc cai. Chay console mode.")
            print("[HW] Cai bang: pip install pyserial")
            return

        try:
            self.arduino = serial.Serial(
                config.ARDUINO_PORT,
                config.ARDUINO_BAUD,
                timeout=1
            )
            time.sleep(2)  # Cho Arduino reset sau khi mo serial
            self.connected = True
            print(f"[HW] Arduino connected on {config.ARDUINO_PORT}")
        except Exception as e:
            self.arduino = None
            self.connected = False
            if config.HARDWARE_ENABLED == "true":
                # User yeu cau bat buoc HW -> raise loi
                raise RuntimeError(
                    f"HARDWARE_ENABLED=true nhung khong ket noi duoc Arduino: {e}"
                )
            print(f"[HW] Khong ket noi duoc Arduino ({config.ARDUINO_PORT}): {e}")
            print(f"[HW] Chay console mode (fallback).")

    def signal_success(self, name=""):
        """Bao diem danh thanh cong. LED xanh + buzzer ngan + LCD."""
        self._send("G", f"SUCCESS - {name}")

    def signal_unknown(self):
        """
        Bao khong nhan dien. LED do + buzzer dai.
        CO THROTTLE: chi gui lai sau HARDWARE_UNKNOWN_COOLDOWN_SEC giay,
        tranh spam buzzer khi mat la trong frame lien tuc.
        """
        now = time.time()
        if now - self._last_unknown_signal_time < config.HARDWARE_UNKNOWN_COOLDOWN_SEC:
            return  # Bo qua, chua het cooldown
        self._last_unknown_signal_time = now
        self._send("R", "UNKNOWN")

    def _send(self, cmd, label):
        """Gui 1 byte lenh xuong Arduino. Hoac in console neu khong co HW."""
        # Khong gui lien tiep cung 1 lenh (it nhat cach nhau 0.5s)
        # -> Bao ve Arduino khoi tin hieu chong cheo
        if self.connected and self.arduino is not None:
            try:
                self.arduino.write(cmd.encode("ascii"))
                self.arduino.flush()
                print(f"[HW] Sent '{cmd}' ({label})")
            except Exception as e:
                print(f"[HW] Loi gui serial: {e}")
                self.connected = False
        else:
            # Console fallback mode
            icon = "🟢" if cmd == "G" else "🔴"
            print(f"[HW-SIM] {icon} {label}")

    def close(self):
        if self.arduino is not None:
            try:
                self.arduino.close()
                print("[HW] Arduino disconnected")
            except Exception:
                pass


if __name__ == "__main__":
    # Test nhanh
    print("Test HardwareController...")
    hw = HardwareController()
    print("\n1. Gui SUCCESS:")
    hw.signal_success("TestUser")
    time.sleep(2)

    print("\n2. Gui UNKNOWN:")
    hw.signal_unknown()
    time.sleep(1)

    print("\n3. Gui UNKNOWN lien tiep (phai bi throttle):")
    for i in range(5):
        hw.signal_unknown()
        time.sleep(0.3)

    print("\n4. Gui SUCCESS lan 2:")
    hw.signal_success("TestUser2")
    time.sleep(2)

    hw.close()
    print("Done.")

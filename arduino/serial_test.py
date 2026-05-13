"""
serial_test.py - Test gui lenh serial xuong Arduino bang tay.
Dung trong giai doan debug truoc khi tich hop voi main.py.

CHAY tu folder goc:
    python arduino/serial_test.py
"""

import serial
import time
import sys
import os

# Cho phep import config tu folder cha
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

PORT = config.ARDUINO_PORT
BAUD = config.ARDUINO_BAUD

print(f"Ket noi Arduino tai {PORT}...")
arduino = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)


def recognized():
    print("Recognized -> GREEN")
    arduino.write(b'G')


def not_recognized():
    print("Not recognized -> RED")
    arduino.write(b'R')


while True:
    cmd = input("Nhap 1 (recognized), 0 (not), Q (quit): ").strip()

    if cmd == "1":
        recognized()
    elif cmd == "0":
        not_recognized()
    elif cmd.upper() == "Q":
        break
    else:
        print("Lenh khong hop le")

arduino.close()
print("Da dong ket noi.")
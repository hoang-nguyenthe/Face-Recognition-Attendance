# SLOT4 - Hardware Integration Module

This folder contains the hardware implementation for the **Face Recognition Attendance System**.

Slot 4 is responsible for connecting the software recognition result to physical output devices using Arduino. The hardware gives immediate feedback when a face is recognized successfully or rejected as unknown.

## 1. Module Responsibility

The Slot 4 module handles:

- USB webcam hardware preparation
- Arduino Uno R3 hardware output
- Green LED for successful recognition
- Red LED for failed or unknown recognition
- Buzzer feedback
- LCD1602 I2C display feedback
- Serial communication between Python and Arduino
- Circuit setup, testing, and documentation

The final hardware receives simple serial commands from Python:

| Command | Meaning | Hardware Output |
|---|---|---|
| `G` | Recognized / attendance success | Green LED, short beep, LCD welcome message |
| `R` | Unknown / recognition failed | Red LED, long beep, LCD unknown message |

## 2. Hardware Components

The setup uses:

- Arduino Uno R3
- USB webcam
- Breadboard
- Green LED
- Red LED
- Active buzzer
- LCD1602 with I2C module
- 220 ohm resistors for LEDs
- Jumper wires
- USB cable for Arduino connection

## 3. Circuit Connection

### LED and Buzzer Pins

| Component | Arduino Pin |
|---|---|
| Green LED | D8 |
| Red LED | D9 |
| Buzzer | D10 |

### LED Wiring

Each LED is connected using a current-limiting resistor.

```text
Arduino digital pin -> LED long leg
LED short leg -> 220 ohm resistor -> GND
```

For this project:

```text
D8 -> green LED long leg
green LED short leg -> 220 ohm resistor -> GND

D9 -> red LED long leg
red LED short leg -> 220 ohm resistor -> GND
```

### Buzzer Wiring

```text
D10 -> buzzer positive pin
GND -> buzzer negative pin
```

## 4. LCD1602 I2C Connection

The LCD1602 display uses an I2C module.

| LCD I2C Pin | Arduino Pin |
|---|---|
| VCC | 5V |
| GND | GND |
| SDA | A4 |
| SCL | A5 |

The I2C address used in the Arduino code is:

```cpp
0x27
```

If the LCD backlight turns on but no text is visible, adjust the small contrast screw on the I2C module.

## 5. Arduino Code

The Arduino source code is located at:

```text
arduino/slot4_system/slot4_system.ino
```

The Arduino listens to serial input at:

```text
9600 baud
```

Before running any Python script that controls the Arduino, upload `slot4_system.ino` to the Arduino using Arduino IDE.

## 6. Arduino Behavior

When Arduino receives `G`:

- Green LED turns on
- Red LED turns off
- Buzzer plays a short beep
- LCD shows a welcome or recognized message

When Arduino receives `R`:

- Red LED turns on
- Green LED turns off
- Buzzer plays a longer beep
- LCD shows an unknown or try-again message

## 7. Python Test Programs

The Slot 4 folder includes Python scripts for testing hardware before full integration.

### 7.1 Serial Test

This script manually sends commands to Arduino.

Example:

```bash
python serial_test.py
```

Input:

```text
G
```

Expected result:

- Green LED turns on
- Short beep
- LCD shows recognized message

Input:

```text
R
```

Expected result:

- Red LED turns on
- Long beep
- LCD shows unknown message

### 7.2 Camera Control Test

This script tests webcam input and Arduino output without real face recognition.

Example:

```bash
python camera_control.py
```

The script checks camera brightness:

- Bright frame -> sends `G`
- Dark frame -> sends `R`

This confirms that Python can read webcam input and send serial commands to Arduino.

## 8. COM Port Configuration

The Arduino was tested on:

```text
COM7
```

If the Arduino appears on another COM port, update the Python script.

Example:

```python
PORT = "COM7"
```

Change it to the correct port, such as:

```python
PORT = "COM5"
```

The COM port can be checked in Arduino IDE:

```text
Tools -> Port
```

## 9. Running Slot 4 Hardware Test

Recommended order:

1. Plug in the Arduino.
2. Upload `slot4_system.ino` to Arduino.
3. Close Arduino IDE Serial Monitor.
4. Check that the LCD shows the ready message.
5. Activate the Python environment if needed.
6. Run the serial or camera test script.

Example:

```bash
python serial_test.py
```

or:

```bash
python camera_control.py
```

## 10. Important Notes

- Arduino IDE Serial Monitor must be closed before running Python serial scripts.
- If Serial Monitor is open, Python may not be able to access the COM port.
- If LEDs do not turn on, check LED polarity:
  - Long leg = positive / Arduino pin side
  - Short leg = negative / resistor to GND side
- If the buzzer works but LEDs do not, check the LED legs, breadboard contact, resistor connection, and GND rail.
- If the LCD is lit but blank, adjust the contrast screw.

## 11. Troubleshooting

### Problem: Python cannot connect to Arduino

Possible causes:

- Arduino is unplugged
- Wrong COM port
- Arduino IDE Serial Monitor is open
- Another program is using the COM port

Fix:

1. Check Arduino IDE -> Tools -> Port.
2. Close Serial Monitor.
3. Update the Python COM port.
4. Run the script again.

### Problem: Buzzer works but LEDs do not

Possible causes:

- LED legs are reversed
- LED legs have weak contact or are rusty
- Resistor is not connected to GND
- LED is connected to the wrong pin

Fix:

- Replace or reseat the LEDs.
- Confirm green LED uses D8.
- Confirm red LED uses D9.
- Confirm Arduino GND is connected to the breadboard GND rail.

### Problem: LCD shows no text

Possible causes:

- Wrong I2C address
- Contrast too low
- SDA/SCL wires are wrong

Fix:

- Confirm LCD address is `0x27`.
- Confirm SDA = A4 and SCL = A5.
- Adjust the contrast screw.

## 12. Current Status

The Slot 4 hardware module has been tested successfully.

Working features:

- USB webcam works
- Arduino serial communication works
- Green LED output works
- Red LED output works
- Buzzer output works
- LCD1602 I2C output works
- Python can send `G` and `R` commands to Arduino
- Hardware can be controlled by camera-based Python logic
- Hardware is ready for integration with the face recognition attendance system

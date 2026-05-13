#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

int greenLED = 8;
int redLED = 9;
int buzzer = 10;

void setup() {
  Serial.begin(9600);

  pinMode(greenLED, OUTPUT);
  pinMode(redLED, OUTPUT);
  pinMode(buzzer, OUTPUT);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("System Ready");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();

    lcd.clear();

    if (cmd == 'G') {
      // SUCCESS
      digitalWrite(greenLED, HIGH);
      digitalWrite(redLED, LOW);

      lcd.setCursor(0, 0);
      lcd.print("Welcome!");
      lcd.setCursor(0, 1);
      lcd.print("Recognized");

      tone(buzzer, 1000, 200);
      delay(1000);

      digitalWrite(greenLED, LOW);
    }

    if (cmd == 'R') {
      // FAIL
      digitalWrite(greenLED, LOW);
      digitalWrite(redLED, HIGH);

      lcd.setCursor(0, 0);
      lcd.print("Unknown");
      lcd.setCursor(0, 1);
      lcd.print("Try Again");

      tone(buzzer, 500, 800);
      delay(1000);

      digitalWrite(redLED, LOW);
    }
  }
}
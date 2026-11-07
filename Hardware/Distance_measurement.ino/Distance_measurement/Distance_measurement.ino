
/*
  Project Name : DistaSense AI
  Module       : Digital Distance Meter
  Controller   : ESP32
  Sensor       : HC-SR04 Ultrasonic Sensor
  Display      : 16x2 I2C LCD
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Ultrasonic sensor pins
#define TRIG_PIN 5
#define ECHO_PIN 18

// Initialize LCD (I2C address: 0x27)
LiquidCrystal_I2C lcd(0x27, 16, 2);


void setup() {

  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  lcd.init();
  lcd.backlight();


  lcd.setCursor(0, 0);
  lcd.print("   DistaSense  ");

  lcd.setCursor(0, 1);
  lcd.print("  Digital Meter ");

  delay(2000);
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("System Ready!");

  lcd.setCursor(0, 1);
  lcd.print("Measuring...");

  delay(2000);
  lcd.clear();
}


// MAIN LOOP
void loop() {

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Read Echo pulse duration
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);

  if (duration == 0) {

    lcd.setCursor(0, 0);
    lcd.print("No Echo Received");

    lcd.setCursor(0, 1);
    lcd.print("Check Object... ");

    Serial.println("No Echo Received!");

  }

  else {

    // Calculate distance in centimetres
    float distance = duration * 0.0343 / 2;

    // Display project name
    lcd.setCursor(0, 0);
    lcd.print("   DistaSense   ");

    // Display measured distance
    lcd.setCursor(0, 1);
    lcd.print("Dist : ");
    lcd.print(distance, 1);
    lcd.print(" cm    ");

    // Display readings on Serial Monitor
    Serial.print("Distance: ");
    Serial.print(distance, 1);
    Serial.println(" cm");

  }
  delay(1000);
}

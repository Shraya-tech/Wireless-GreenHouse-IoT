// ESP32 Dev Module Pins
const int sensorPin = 34; // Connect your soil sensor signal to GPIO 34
const int ledPin = 2;     // Built-in Blue LED on the Dev Module

void setup() {
  Serial.begin(9600);    // Matches the speed in your app.py
  pinMode(ledPin, OUTPUT);
}

void loop() {
  int sensorValue = analogRead(sensorPin); // Read moisture level
  
  // Sending the "DATA:" flag so Python knows to grab the number
  Serial.print("DATA:"); 
  Serial.println(sensorValue);

  // If the sensor is dry, turn on the built-in LED [cite: 10]
  if (sensorValue > 800) {
    digitalWrite(ledPin, HIGH);
  } else {
    digitalWrite(ledPin, LOW);
  }
  
  delay(200); // Send data 5 times per second [cite: 11]
}
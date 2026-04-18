#include <esp_sleep.h>

#define uS_TO_S_FACTOR 1000000ULL 
#define SLEEP_SECONDS 10          // Quick sleep for the demo

const int sensorPin = 34;
const int ledPin = 2; 

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
  delay(1000); 

  // 1. WAKE & SENSE
  int sensorValue = analogRead(sensorPin);
  
  // 2. SEND TO PYTHON DASHBOARD
  Serial.print("DATA:");
  Serial.println(sensorValue);

  // 3. ACTION (LED stays on for 3 seconds so David can see it)
  if (sensorValue > 800) {
    digitalWrite(ledPin, HIGH);
    delay(3000); 
    digitalWrite(ledPin, LOW);
  }

  // 4. ENTER DEEP SLEEP
  Serial.println("DATA:Sleeping for 10s...");
  esp_sleep_enable_timer_wakeup(SLEEP_SECONDS * uS_TO_S_FACTOR);
  Serial.flush(); 
  esp_deep_sleep_start();
}

void loop() {} // Not used in Deep Sleep
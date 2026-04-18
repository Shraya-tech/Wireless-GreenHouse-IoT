void setup() {
  Serial.begin(9600); 
  pinMode(13, OUTPUT);
}

void loop() {
  int sensorValue = analogRead(A0); // Reading the wire in A0
  
  // Python looks for the word "DATA:" to know a number is coming
  Serial.print("DATA:"); 
  Serial.println(sensorValue);

  if (sensorValue > 400) {
    digitalWrite(13, HIGH); // Turn on LED if touched/dry
  } else {
    digitalWrite(13, LOW);
  }
  delay(200); // Send data 5 times a second
}
void setup() {
  Serial.begin(112500);
}

void loop() {
    int selectedPin = Serial.parseInt();
    int pinValue = digitalRead(selectedPin);
    Serial.println(pinValue);
}

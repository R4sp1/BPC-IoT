
#define VOLTAGE_PIN 12
#define NB_IOT_RESET_PIN 35

void setup() {
  Serial.begin(9600);
  Serial2.begin(9600);

  pinMode(VOLTAGE_PIN, OUTPUT);
  digitalWrite(VOLTAGE_PIN, HIGH);
  pinMode(NB_IOT_RESET_PIN, OUTPUT);
  digitalWrite(NB_IOT_RESET_PIN, LOW);
}

void loop() {
  while (Serial2.available()) {
    Serial.write(Serial2.read());
  }
  while (Serial.available()) {
    Serial2.write(Serial.read());
  }
}
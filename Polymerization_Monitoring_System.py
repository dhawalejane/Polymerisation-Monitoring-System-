// Polymerization Monitoring System - FIXED VERSION
// Sensors: DHT11/22, LDR, Turbidity Sensor

#include <DHT.h>

// Pin Definitions
#define DHTPIN 2          // DHT sensor pin
#define DHTTYPE DHT11     // Try DHT11 first, change to DHT22 if you have that
#define LDR_PIN A0        // LDR analog pin
#define LED_PIN 13        // Changed to pin 13 (has built-in LED too)
#define TURBIDITY_PIN A1  // Turbidity sensor analog pin

// Initialize DHT sensor
DHT dht(DHTPIN, DHTTYPE);

// Variables
unsigned long previousMillis = 0;
const long interval = 2000;  // Reading interval (2 seconds for DHT11)
unsigned long startTime = 0;

// Baseline values
int ldrBaseline = 0;
int turbidityBaseline = 0;

void setup() {
  Serial.begin(9600);
  
  // Initialize LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // Turn on LED
  
  // Initialize DHT
  dht.begin();
  
  Serial.println("=== Aniline Polymerization Monitor ===");
  Serial.println("Waiting for sensors to stabilize...");
  
  // Longer delay for DHT to stabilize
  delay(3000);
  
  // Test LED
  Serial.println("Testing LED...");
  for(int i = 0; i < 3; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(200);
    digitalWrite(LED_PIN, LOW);
    delay(200);
  }
  digitalWrite(LED_PIN, HIGH); // Keep LED on
  
  // Calibration
  calibrateSensors();
  
  // CSV Header
  Serial.println("\n--- DATA START ---");
  Serial.println("Time(s),Temp(C),Humidity(%),LDR,LDR_Change(%),Turbidity,Color_Index");
  
  startTime = millis();
}

void loop() {
  unsigned long currentMillis = millis();
  
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
    float elapsedTime = (currentMillis - startTime) / 1000.0;
    readAndLogData(elapsedTime);
  }
}

void calibrateSensors() {
  Serial.println("\nCalibrating...");
  delay(2000);
  
  // Multiple readings for baseline
  long ldrSum = 0;
  long turbiditySum = 0;
  int samples = 20;
  
  Serial.println("Taking baseline readings...");
  for (int i = 0; i < samples; i++) {
    ldrSum += analogRead(LDR_PIN);
    turbiditySum += analogRead(TURBIDITY_PIN);
    delay(100);
  }
  
  ldrBaseline = ldrSum / samples;
  turbidityBaseline = turbiditySum / samples;
  
  Serial.print("LDR Baseline: ");
  Serial.println(ldrBaseline);
  Serial.print("Turbidity Baseline: ");
  Serial.println(turbidityBaseline);
  Serial.println("Calibration Done!\n");
}

void readAndLogData(float timeStamp) {
  // Read DHT - with error handling
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Read LDR
  int ldrValue = analogRead(LDR_PIN);
  
  // Read Turbidity
  int turbidityRaw = analogRead(TURBIDITY_PIN);
  
  // Calculate changes
  float ldrChange = 0;
  if (ldrBaseline > 0) {
    ldrChange = ((float)(ldrBaseline - ldrValue) / ldrBaseline) * 100.0;
  }
  
  float colorIndex = map(ldrValue, ldrBaseline, 0, 0, 100);
  colorIndex = constrain(colorIndex, 0, 100);
  
  // Print time
  Serial.print(timeStamp, 1);
  Serial.print(",");
  
  // Check DHT errors
  if (isnan(temperature)) {
    Serial.print("DHT_ERROR");
  } else {
    Serial.print(temperature, 1);
  }
  Serial.print(",");
  
  if (isnan(humidity)) {
    Serial.print("DHT_ERROR");
  } else {
    Serial.print(humidity, 1);
  }
  Serial.print(",");
  
  // Print other sensor values
  Serial.print(ldrValue);
  Serial.print(",");
  Serial.print(ldrChange, 1);
  Serial.print(",");
  Serial.print(turbidityRaw);
  Serial.print(",");
  Serial.println(colorIndex, 1);
  
  // Debug info every 10 readings
  static int counter = 0;
  counter++;
  if (counter >= 10) {
    Serial.print("DEBUG - LDR:");
    Serial.print(ldrValue);
    Serial.print(" Turb:");
    Serial.print(turbidityRaw);
    Serial.print(" LED:");
    Serial.println(digitalRead(LED_PIN) ? "ON" : "OFF");
    counter = 0;
  }
}

/*
 * IoT Multi-Rubro System - ESP32 Firmware
 * ========================================
 * Modular firmware for ESP32-based sensor nodes
 * Supports multiple sensor types and communication protocols
 * 
 * Author: IoT Multi-Rubro Team
 * Version: 1.0.0
 * Platform: ESP32 (Arduino Framework)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

// ============================================
// GLOBAL VARIABLES
// ============================================
WiFiClient wifiClient;
HTTPClient http;

// Sensor readings
float temperatureValue = 0.0;
float humidityValue = 0.0;
float sensorValue = 0.0;

// Timing
unsigned long lastSensorRead = 0;
unsigned long lastDataSend = 0;
const unsigned long SENSOR_INTERVAL = 1000;  // Read sensors every 1s
const unsigned long SEND_INTERVAL = 5000;    // Send data every 5s

// Device info
String deviceId = DEVICE_ID;
String deviceType = DEVICE_TYPE;

// ============================================
// SETUP
// ============================================
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  printBanner();
  
  // Initialize hardware
  initSensors();
  
  // Connect to WiFi
  connectWiFi();
  
  // Register device with backend
  registerDevice();
  
  Serial.println("\n[READY] Device initialized successfully");
  Serial.println("========================================");
}

// ============================================
// MAIN LOOP
// ============================================
void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WARN] WiFi disconnected, reconnecting...");
    connectWiFi();
  }
  
  // Read sensors at interval
  if (millis() - lastSensorRead >= SENSOR_INTERVAL) {
    readSensors();
    lastSensorRead = millis();
  }
  
  // Send data at interval
  if (millis() - lastDataSend >= SEND_INTERVAL) {
    sendDataToBackend();
    lastDataSend = millis();
  }
  
  // Small delay to prevent watchdog issues
  delay(10);
}

// ============================================
// WIFI FUNCTIONS
// ============================================
void connectWiFi() {
  Serial.println("\n[WiFi] Connecting to: " + String(WIFI_SSID));
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Connected!");
    Serial.println("[WiFi] IP: " + WiFi.localIP().toString());
    Serial.println("[WiFi] RSSI: " + String(WiFi.RSSI()) + " dBm");
  } else {
    Serial.println("\n[ERROR] WiFi connection failed!");
  }
}

// ============================================
// SENSOR FUNCTIONS
// ============================================
void initSensors() {
  Serial.println("\n[SENSOR] Initializing sensors...");
  
  // Initialize based on device type
  if (deviceType == "temperature") {
    // Initialize temperature sensor (DS18B20, DHT22, etc.)
    Serial.println("[SENSOR] Temperature sensor initialized");
  } 
  else if (deviceType == "humidity") {
    // Initialize humidity sensor
    Serial.println("[SENSOR] Humidity sensor initialized");
  }
  else if (deviceType == "motion") {
    // Initialize PIR sensor
    pinMode(SENSOR_PIN, INPUT);
    Serial.println("[SENSOR] Motion sensor initialized");
  }
  else {
    Serial.println("[SENSOR] Generic sensor initialized");
  }
}

void readSensors() {
  // Read sensor based on type
  if (deviceType == "temperature") {
    sensorValue = readTemperature();
  }
  else if (deviceType == "humidity") {
    sensorValue = readHumidity();
  }
  else if (deviceType == "motion") {
    sensorValue = readMotion();
  }
  else {
    // Generic analog reading
    sensorValue = analogRead(SENSOR_PIN) * SENSOR_SCALE;
  }
  
  Serial.printf("[SENSOR] Read: %.2f %s\n", sensorValue, SENSOR_UNIT);
}

float readTemperature() {
  // [Simulation] Generate realistic temperature reading
  // In real hardware, use actual sensor library (e.g., DHT.h, OneWire.h)
  
  #ifdef SIMULATE_SENSOR
    float baseTemp = 20.0 + random(-50, 50) / 10.0;
    return baseTemp;
  #else
    // Example: Read from DHT22
    // return dht.readTemperature();
    return 0.0;
  #endif
}

float readHumidity() {
  #ifdef SIMULATE_SENSOR
    float baseHum = 60.0 + random(-100, 100) / 10.0;
    return constrain(baseHum, 0, 100);
  #else
    // Example: Read from DHT22
    // return dht.readHumidity();
    return 0.0;
  #endif
}

float readMotion() {
  #ifdef SIMULATE_SENSOR
    return random(0, 100) < 10 ? 1.0 : 0.0;  // 10% probability
  #else
    return digitalRead(SENSOR_PIN);
  #endif
}

// ============================================
// BACKEND COMMUNICATION
// ============================================
void registerDevice() {
  Serial.println("\n[API] Registering device with backend...");
  
  String url = String(API_BASE_URL) + "/api/devices";
  
  // Create JSON payload
  StaticJsonDocument<512> doc;
  doc["device_id"] = deviceId;
  doc["name"] = DEVICE_NAME;
  doc["device_type"] = deviceType;
  doc["rubro"] = DEVICE_RUBRO;
  doc["location"] = DEVICE_LOCATION;
  
  String payload;
  serializeJson(doc, payload);
  
  // Send HTTP POST
  http.begin(wifiClient, url);
  http.addHeader("Content-Type", "application/json");
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 201 || httpCode == 400) {  // 201=Created, 400=Already exists
    Serial.println("[API] Device registered successfully");
  } else {
    Serial.printf("[ERROR] Registration failed: %d\n", httpCode);
  }
  
  http.end();
}

void sendDataToBackend() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WARN] No WiFi, skipping data send");
    return;
  }
  
  String url = String(API_BASE_URL) + "/api/data";
  
  // Create JSON payload
  StaticJsonDocument<256> doc;
  doc["device_id"] = deviceId;
  doc["value"] = sensorValue;
  doc["unit"] = SENSOR_UNIT;
  doc["quality"] = 1.0;
  
  String payload;
  serializeJson(doc, payload);
  
  // Send HTTP POST
  http.begin(wifiClient, url);
  http.addHeader("Content-Type", "application/json");
  
  int httpCode = http.POST(payload);
  
  if (httpCode == 201) {
    Serial.printf("[API] Data sent: %.2f %s\n", sensorValue, SENSOR_UNIT);
  } else {
    Serial.printf("[ERROR] Send failed: %d\n", httpCode);
  }
  
  http.end();
}

// ============================================
// UTILITY FUNCTIONS
// ============================================
void printBanner() {
  Serial.println("\n========================================");
  Serial.println("  IoT Multi-Rubro - ESP32 Node");
  Serial.println("========================================");
  Serial.println("Device ID:   " + deviceId);
  Serial.println("Device Type: " + deviceType);
  Serial.println("Rubro:       " + String(DEVICE_RUBRO));
  Serial.println("Version:     " + String(FIRMWARE_VERSION));
  Serial.println("========================================");
}

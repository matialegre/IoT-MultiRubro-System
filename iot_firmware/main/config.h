/*
 * IoT Multi-Rubro - ESP32 Configuration
 * ======================================
 * Hardware and network configuration
 */

#ifndef CONFIG_H
#define CONFIG_H

// ============================================
// FIRMWARE VERSION
// ============================================
#define FIRMWARE_VERSION "1.0.0"

// ============================================
// DEVICE CONFIGURATION
// ============================================
// Change these values for each device
#define DEVICE_ID "ESP32-001"
#define DEVICE_NAME "ESP32 Sensor Node"
#define DEVICE_TYPE "temperature"  // temperature, humidity, motion, etc.
#define DEVICE_RUBRO "carniceria"  // carniceria, riego, bar, etc.
#define DEVICE_LOCATION "Main Room"

// ============================================
// NETWORK CONFIGURATION
// ============================================
// WiFi credentials
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// Backend API
#define API_BASE_URL "http://192.168.1.100:8000"  // Change to your server IP

// MQTT (Optional)
#define MQTT_BROKER "192.168.1.100"
#define MQTT_PORT 1883
#define MQTT_TOPIC_DATA "iot/data"
#define MQTT_TOPIC_STATUS "iot/status"

// ============================================
// HARDWARE PINS
// ============================================
// Sensor pins (adjust based on your wiring)
#define SENSOR_PIN 34         // ADC1 channel
#define DHT_PIN 4             // DHT22 data pin
#define PIR_PIN 5             // PIR motion sensor
#define LED_PIN 2             // Built-in LED
#define RELAY_PIN 25          // Relay control

// I2C pins (for advanced sensors)
#define I2C_SDA 21
#define I2C_SCL 22

// ============================================
// SENSOR CALIBRATION
// ============================================
#define SENSOR_SCALE 1.0      // Scaling factor
#define SENSOR_OFFSET 0.0     // Offset calibration
#define SENSOR_UNIT "units"   // Measurement unit

// Temperature sensor (DS18B20, DHT22)
#define TEMP_OFFSET 0.0       // Calibration offset (°C)

// Humidity sensor
#define HUM_OFFSET 0.0        // Calibration offset (%)

// Analog sensors
#define ADC_RESOLUTION 4096   // 12-bit ADC
#define ADC_VOLTAGE 3.3       // Reference voltage

// ============================================
// TIMING CONFIGURATION
// ============================================
#define SENSOR_READ_INTERVAL 1000     // Read sensors every 1s (ms)
#define DATA_SEND_INTERVAL 5000       // Send data every 5s (ms)
#define HEARTBEAT_INTERVAL 30000      // Send heartbeat every 30s (ms)
#define RECONNECT_DELAY 5000          // WiFi reconnect delay (ms)

// ============================================
// OPERATION MODE
// ============================================
// Uncomment to enable sensor simulation
#define SIMULATE_SENSOR

// Uncomment to enable debug output
#define DEBUG_MODE

// Uncomment to use MQTT instead of HTTP
// #define USE_MQTT

// ============================================
// POWER MANAGEMENT
// ============================================
#define ENABLE_DEEP_SLEEP false       // Enable deep sleep mode
#define SLEEP_DURATION 60             // Deep sleep duration (seconds)
#define BATTERY_PIN 35                // Battery voltage monitor pin

// ============================================
// OTA UPDATES
// ============================================
#define ENABLE_OTA true               // Enable Over-The-Air updates
#define OTA_PASSWORD "iot-update"     // OTA password

// ============================================
// SECURITY
// ============================================
// API authentication (if enabled on backend)
#define API_KEY ""                    // Leave empty if not used

#endif // CONFIG_H

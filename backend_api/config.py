"""
Global Configuration Module
============================
Central configuration for the IoT Multi-Rubro System.
Toggle between simulation and real hardware mode.
"""

import os
from typing import Dict, Any

# ============================================
# OPERATION MODE
# ============================================
# Set to True for simulation (synthetic data)
# Set to False for real ESP32 hardware
SIM_MODE = True

# ============================================
# DATABASE CONFIGURATION
# ============================================
if SIM_MODE:
    DATABASE_URL = "sqlite:///./iot_multirubro.db"
else:
    # Production SQL Server (configure as needed)
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mssql+pyodbc://user:pass@localhost/iot_db?driver=ODBC+Driver+17+for+SQL+Server"
    )

# ============================================
# API CONFIGURATION
# ============================================
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "IoT Multi-Rubro API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "Enterprise IoT automation system for multiple commercial sectors"

# CORS settings
CORS_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]

# JWT Authentication
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ============================================
# IoT NETWORK CONFIGURATION
# ============================================
if SIM_MODE:
    # Simulator configuration
    SIMULATOR_UPDATE_RATE = 1.0  # seconds
    SIMULATOR_NOISE_LEVEL = 0.05  # 5% noise
    SIMULATOR_DEVICE_COUNT = 5
else:
    # ESP32 real network configuration
    ESP32_UDP_PORT = 8888
    ESP32_MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
    ESP32_MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    ESP32_DISCOVERY_TIMEOUT = 30  # seconds

# ============================================
# SENSOR PHYSICAL LIMITS
# ============================================
SENSOR_LIMITS: Dict[str, Dict[str, float]] = {
    "temperature": {"min": -40.0, "max": 125.0, "unit": "°C"},
    "humidity": {"min": 0.0, "max": 100.0, "unit": "%"},
    "pressure": {"min": 300.0, "max": 1100.0, "unit": "hPa"},
    "weight": {"min": 0.0, "max": 500.0, "unit": "kg"},
    "flow": {"min": 0.0, "max": 100.0, "unit": "L/min"},
    "luminosity": {"min": 0.0, "max": 100000.0, "unit": "lux"},
    "motion": {"min": 0, "max": 1, "unit": "bool"},
    "distance": {"min": 2.0, "max": 400.0, "unit": "cm"},
    "noise": {"min": 30.0, "max": 130.0, "unit": "dB"},
    "soil_moisture": {"min": 0.0, "max": 100.0, "unit": "%"},
}

# ============================================
# INDUSTRY-SPECIFIC PRESETS
# ============================================
RUBRO_PRESETS: Dict[str, Dict[str, Any]] = {
    "carniceria": {
        "name": "Butcher Shop / Bakery",
        "sensors": ["temperature", "humidity", "door_state"],
        "critical_temp_min": -18,
        "critical_temp_max": -15,
        "alert_delay": 300,  # 5 minutes
    },
    "tienda_ropa": {
        "name": "Clothing Store",
        "sensors": ["motion", "luminosity", "people_count"],
        "business_hours": {"open": 9, "close": 21},
        "auto_lighting": True,
    },
    "centro_medico": {
        "name": "Medical Center",
        "features": ["appointments", "notifications"],
        "appointment_duration": 30,  # minutes
        "reminder_hours": 24,
    },
    "bar_boliche": {
        "name": "Bar / Nightclub",
        "features": ["rfid_cards", "pos", "inventory"],
        "currency": "ARS",
        "card_types": ["cliente", "staff", "vip"],
    },
    "riego": {
        "name": "Irrigation System",
        "sensors": ["soil_moisture", "rain", "tank_level", "temperature"],
        "actuators": ["valve", "pump"],
        "schedule": [{"hour": 6, "duration": 30}, {"hour": 18, "duration": 30}],
    },
}

# ============================================
# ALERTING CONFIGURATION
# ============================================
ALERT_CHANNELS = {
    "email": {"enabled": SIM_MODE, "smtp_server": "localhost"},
    "whatsapp": {"enabled": False, "api_key": ""},  # Simulated
    "telegram": {"enabled": False, "bot_token": ""},  # Simulated
    "webhook": {"enabled": True, "url": ""},
}

ALERT_SEVERITIES = ["info", "warning", "error", "critical"]

# ============================================
# LOGGING CONFIGURATION
# ============================================
LOG_LEVEL = "INFO" if SIM_MODE else "DEBUG"
LOG_FILE = "iot_multirubro.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# ============================================
# WEBSOCKET CONFIGURATION
# ============================================
WS_HEARTBEAT_INTERVAL = 30  # seconds
WS_MAX_CONNECTIONS = 100

# ============================================
# REPORT GENERATION
# ============================================
REPORT_OUTPUT_DIR = "../reports/"
REPORT_FORMATS = ["csv", "pdf", "json"]
REPORT_RETENTION_DAYS = 90

# ============================================
# PERFORMANCE TUNING
# ============================================
MAX_DATAPOINTS_PER_QUERY = 10000
DATA_RETENTION_DAYS = 365
BATCH_INSERT_SIZE = 100

# ============================================
# VALIDATION & TESTING
# ============================================
if SIM_MODE:
    VALIDATION_DURATION = 600  # 10 minutes
    VALIDATION_SENSOR_COUNT = 5
    VALIDATION_EVENT_RATE = 0.1  # 10% probability per second

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_sensor_config(sensor_type: str) -> Dict[str, Any]:
    """Get configuration for specific sensor type."""
    return SENSOR_LIMITS.get(sensor_type, {})


def get_rubro_config(rubro: str) -> Dict[str, Any]:
    """Get industry-specific configuration."""
    return RUBRO_PRESETS.get(rubro, {})


def is_simulation_mode() -> bool:
    """Check if system is in simulation mode."""
    return SIM_MODE


# ============================================
# STARTUP BANNER
# ============================================
def print_startup_info():
    """Print system configuration on startup."""
    mode = "🔄 SIMULATION MODE" if SIM_MODE else "🔌 HARDWARE MODE"
    print("=" * 60)
    print(f"  IoT Multi-Rubro System v{API_VERSION}")
    print(f"  {mode}")
    print(f"  API: http://{API_HOST}:{API_PORT}")
    print(f"  Database: {DATABASE_URL.split('://')[0]}")
    print("=" * 60)

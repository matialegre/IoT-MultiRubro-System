# IoT Multi-Rubro Automation System

## 🎯 Overview

Enterprise-grade IoT automation ecosystem adaptable to multiple commercial sectors (gastronomy, retail, medical, recreational, industrial). Combines ESP32 hardware, modular backend, and responsive Web/App interface.

**Key Feature:** Full simulation mode - entire system runs without physical hardware by toggling `SIM_MODE = True`.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     WEB DASHBOARD (PWA)                      │
│              Bootstrap 5 + Chart.js + WebSocket              │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API / WebSocket
┌────────────────────────▼────────────────────────────────────┐
│                   BACKEND API (FastAPI)                      │
│        Device Management | Rules Engine | Alerts             │
└─────┬──────────────────┬─────────────────────┬──────────────┘
      │                  │                     │
┌─────▼──────┐  ┌────────▼────────┐  ┌────────▼──────────┐
│  Database  │  │  MQTT Broker    │  │  Simulator Engine │
│  SQLite/   │  │  (Optional)     │  │  Physics Models   │
│  SQL Server│  └─────────────────┘  └───────────────────┘
└────────────┘           │
                ┌────────▼─────────┐
                │   ESP32 Nodes    │
                │ Sensors/Actuators│
                └──────────────────┘
```

## 📁 Project Structure

```
IoT-MultiRubro-System/
├── backend_api/              # FastAPI server
│   ├── main.py              # Main application entry
│   ├── config.py            # Global configuration (SIM_MODE)
│   ├── database.py          # DB models and connection
│   ├── api/                 # REST endpoints
│   │   ├── devices.py
│   │   ├── data.py
│   │   ├── rules.py
│   │   ├── alerts.py
│   │   └── users.py
│   ├── services/            # Business logic
│   │   ├── rules_engine.py
│   │   ├── alert_service.py
│   │   └── data_processor.py
│   └── requirements.txt
│
├── iot_firmware/            # ESP32 firmware
│   ├── main/
│   │   ├── main.ino        # Arduino main file
│   │   └── config.h        # Hardware configuration
│   ├── modules/
│   │   ├── sensors.cpp     # Sensor drivers
│   │   ├── actuators.cpp   # Actuator control
│   │   ├── network.cpp     # WiFi/UDP/MQTT
│   │   └── ota.cpp         # OTA updates
│   └── platformio.ini      # PlatformIO config
│
├── simulator/               # Advanced sensor simulator
│   ├── sensor_models.py    # Physical models
│   ├── scenario_player.py  # Timeline executor
│   ├── event_injector.py   # Failure simulation
│   └── mock_devices.py     # Virtual ESP32 nodes
│
├── web_frontend/            # Progressive Web App
│   ├── index.html          # Main dashboard
│   ├── assets/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       ├── dashboard.js
│   │       ├── charts.js
│   │       └── websocket.js
│   ├── manifest.json       # PWA manifest
│   └── service-worker.js   # Offline support
│
├── scenarios/               # Industry-specific configs
│   ├── carniceria.json     # Butcher shop scenario
│   ├── bar_boliche.json    # Bar/nightclub
│   ├── riego.json          # Irrigation system
│   ├── tienda_ropa.json    # Clothing store
│   └── centro_medico.json  # Medical center
│
├── tests/                   # Automated testing
│   ├── test_simulator.py
│   ├── test_api.py
│   ├── test_rules_engine.py
│   └── test_integration.py
│
├── docs/                    # Technical documentation
│   ├── API_REFERENCE.md
│   ├── ARCHITECTURE.md
│   ├── SENSOR_MODELS.md
│   ├── QUICK_START.md
│   └── diagrams/
│       ├── architecture.png
│       └── data_flow.png
│
├── scripts/                 # Utility scripts
│   ├── start_simulation.py
│   ├── validate_system.py
│   └── generate_reports.py
│
├── reports/                 # Auto-generated reports
│   └── .gitkeep
│
└── docker-compose.yml       # Optional containerization
```

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies

```bash
# Backend
cd backend_api
pip install -r requirements.txt

# Frontend (optional, uses CDN by default)
# No installation needed
```

### 2. Start Simulation Mode

```bash
# Windows
python scripts/start_simulation.py

# Linux
python3 scripts/start_simulation.py
```

### 3. Access Dashboard

Open browser: `http://localhost:8000`

**Demo Credentials:**
- User: `admin`
- Pass: `admin123`

## 🎮 Operation Modes

### Simulation Mode (Default)
```python
# backend_api/config.py
SIM_MODE = True  # Generates synthetic sensor data
```

### Real Hardware Mode
```python
# backend_api/config.py
SIM_MODE = False  # Connects to ESP32 nodes via WiFi
```

## 📊 Supported Industries

### 🥩 Butcher Shops / Bakeries
- **Sensors:** Temperature, humidity, door state
- **Features:** Cold chain monitoring, thermal curve history
- **Alerts:** Temperature excursions, power failures

### 👕 Retail / Clothing Stores  
- **Sensors:** People counter (IR/ultrasound), light level
- **Features:** Traffic analytics, automated lighting
- **Reports:** Hourly flow, energy consumption

### 🏥 Medical Centers / Aesthetics / Sports
- **Features:** Online appointment system
- **Integrations:** WhatsApp/Telegram notifications (simulated)
- **Dashboard:** Real-time availability

### 🍺 Bars / Nightclubs
- **System:** RFID/QR rechargeable cards (simulated)
- **Features:** Credit control, sales tracking, inventory
- **Reports:** Daily statistics, loss analysis

### 🌱 Irrigation / Urban Agriculture
- **Control:** Solenoid valves, pumps
- **Sensors:** Soil moisture, rain, tank level
- **Rules:** Scheduled watering + moisture thresholds

## 🔧 Configuration

### Adding New Device
```json
// POST /api/devices
{
  "name": "Freezer-001",
  "type": "temperature_sensor",
  "location": "Main Storage",
  "rubro": "carniceria",
  "config": {
    "min_temp": -18,
    "max_temp": -15,
    "alert_threshold": 2
  }
}
```

### Creating Rule
```json
// POST /api/rules
{
  "name": "High Temperature Alert",
  "condition": {
    "sensor": "Freezer-001",
    "parameter": "temperature",
    "operator": ">",
    "value": -10
  },
  "action": {
    "type": "alert",
    "severity": "critical",
    "message": "Freezer temperature too high!"
  }
}
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/devices` | GET | List all devices |
| `/api/devices` | POST | Register new device |
| `/api/data/{device_id}` | GET | Get sensor readings |
| `/api/rules` | GET/POST | Manage automation rules |
| `/api/alerts` | GET | Get active alerts |
| `/api/reports/export` | GET | Export CSV/PDF |
| `/ws/realtime` | WS | WebSocket live data stream |

## 🧪 Testing & Validation

```bash
# Run automated test suite
python -m pytest tests/ -v

# Validate system (10 min simulation)
python scripts/validate_system.py

# Generate performance report
python scripts/generate_reports.py
```

## 📈 Performance Metrics

- **Latency:** < 50ms (UDP), < 100ms (MQTT)
- **Data Rate:** Up to 100 sensors @ 1Hz
- **Database:** SQLite (10K records/s), SQL Server (production)
- **WebSocket:** 50+ concurrent clients

## 🔐 Security

- JWT authentication for API
- HTTPS/WSS in production
- API key rotation
- SQL injection protection
- XSS sanitization

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewSensor`)
3. Commit changes (`git commit -m 'Add new sensor type'`)
4. Push to branch (`git push origin feature/NewSensor`)
5. Open Pull Request

## 📞 Support

- Documentation: `/docs/`
- Issues: GitHub Issues
- Email: support@iot-multirubro.local

---

**Status:** ✅ Production-ready simulation | 🚧 Hardware integration in progress

**Version:** 1.0.0 | **Last Update:** 2025-01-17

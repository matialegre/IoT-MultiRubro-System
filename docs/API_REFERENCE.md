# 📡 API Reference

## Base URL
```
http://localhost:8000/api
```

## Authentication
Currently using demo mode. In production, use JWT tokens.

---

## 📋 Endpoints

### Health & Status

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "mode": "simulation",
  "timestamp": "2025-01-17T03:33:00Z"
}
```

#### GET /api/stats
System statistics.

**Response:**
```json
{
  "devices": {
    "total": 4,
    "online": 4,
    "offline": 0
  },
  "alerts": {
    "total": 2,
    "critical": 1
  },
  "data": {
    "points_24h": 34560,
    "rate_per_minute": 24.0
  }
}
```

---

### 🔌 Devices

#### GET /api/devices
List all registered devices.

**Query Parameters:**
- `rubro` (optional): Filter by industry sector
- `status` (optional): Filter by status (online/offline)

**Response:**
```json
[
  {
    "id": 1,
    "device_id": "TEMP-001",
    "name": "Freezer Principal",
    "device_type": "temperature",
    "status": "online",
    "last_seen": "2025-01-17T03:30:00Z",
    "is_simulated": true
  }
]
```

#### POST /api/devices
Register new device.

**Request:**
```json
{
  "device_id": "TEMP-002",
  "name": "Sensor Nuevo",
  "device_type": "temperature",
  "rubro": "carniceria",
  "location": "Sala Principal",
  "description": "Sensor de temperatura ambiente",
  "config": {
    "min_temp": -20,
    "max_temp": -15
  }
}
```

**Response:** `201 Created`
```json
{
  "id": 5,
  "device_id": "TEMP-002",
  "name": "Sensor Nuevo",
  "device_type": "temperature",
  "status": "online",
  "is_simulated": true
}
```

#### GET /api/devices/{device_id}
Get device details.

**Response:**
```json
{
  "id": 1,
  "device_id": "TEMP-001",
  "name": "Freezer Principal",
  "device_type": "temperature",
  "rubro": "carniceria",
  "location": "Cámara Frigorífica",
  "status": "online",
  "last_seen": "2025-01-17T03:30:00Z",
  "config": {
    "min_temp": -18,
    "max_temp": -15
  }
}
```

#### DELETE /api/devices/{device_id}
Delete device and all associated data.

**Response:** `200 OK`
```json
{
  "message": "Device deleted successfully"
}
```

---

### 📊 Sensor Data

#### GET /api/data/{device_id}
Get historical sensor readings.

**Query Parameters:**
- `limit` (default: 100): Maximum number of points
- `hours` (optional): Data from last N hours

**Response:**
```json
{
  "device_id": "TEMP-001",
  "device_name": "Freezer Principal",
  "device_type": "temperature",
  "count": 50,
  "data": [
    {
      "timestamp": "2025-01-17T03:25:00Z",
      "value": -17.5,
      "unit": "°C",
      "quality": 1.0
    },
    {
      "timestamp": "2025-01-17T03:26:00Z",
      "value": -17.8,
      "unit": "°C",
      "quality": 1.0
    }
  ]
}
```

#### POST /api/data
Manually post sensor reading.

**Request:**
```json
{
  "device_id": "TEMP-001",
  "value": 22.5,
  "unit": "°C",
  "quality": 1.0
}
```

**Response:** `201 Created`
```json
{
  "message": "Data received",
  "actions_triggered": 1,
  "actions": [
    {
      "type": "alert",
      "severity": "warning",
      "message": "Temperature high"
    }
  ]
}
```

---

### ⚙️ Rules

#### GET /api/rules
List all automation rules.

**Query Parameters:**
- `active_only` (default: false): Show only active rules

**Response:**
```json
[
  {
    "id": 1,
    "name": "Alerta Temperatura Alta",
    "description": "Alertar si temperatura > -10°C",
    "condition": {
      "device_id": "TEMP-001",
      "operator": ">",
      "value": -10.0
    },
    "action": {
      "type": "alert",
      "severity": "critical",
      "message": "Temperatura alta!"
    },
    "is_active": true,
    "priority": 10,
    "last_triggered": "2025-01-17T02:15:00Z",
    "trigger_count": 5
  }
]
```

#### POST /api/rules
Create new automation rule.

**Request:**
```json
{
  "name": "Temperatura Alta",
  "description": "Alerta cuando temperatura sube",
  "condition": {
    "device_id": "TEMP-001",
    "operator": ">",
    "value": 25.0,
    "parameter": "value"
  },
  "action": {
    "type": "alert",
    "severity": "warning",
    "message": "Temperatura: {value}°C"
  },
  "is_active": true,
  "priority": 5,
  "cooldown_seconds": 300
}
```

**Complex Condition (AND logic):**
```json
{
  "name": "Múltiples Condiciones",
  "condition": {
    "and": [
      {"device_id": "TEMP-001", "operator": ">", "value": 25},
      {"device_id": "HUM-001", "operator": "<", "value": 30}
    ]
  },
  "action": {
    "type": "alert",
    "severity": "critical",
    "message": "Temp alta Y humedad baja!"
  }
}
```

**Response:** `201 Created`

#### PUT /api/rules/{rule_id}
Update existing rule.

#### DELETE /api/rules/{rule_id}
Delete rule.

---

### 🚨 Alerts

#### GET /api/alerts
List system alerts.

**Query Parameters:**
- `unresolved_only` (default: false)
- `severity` (optional): info, warning, error, critical
- `limit` (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "device_id": 1,
    "severity": "critical",
    "title": "Alerta Temperatura Alta",
    "message": "Temperatura del freezer: 25.0°C",
    "is_acknowledged": false,
    "is_resolved": false,
    "created_at": "2025-01-17T03:20:00Z"
  }
]
```

#### POST /api/alerts/{alert_id}/acknowledge
Mark alert as acknowledged.

**Response:**
```json
{
  "message": "Alert acknowledged"
}
```

#### POST /api/alerts/{alert_id}/resolve
Mark alert as resolved.

**Response:**
```json
{
  "message": "Alert resolved"
}
```

---

## 🔌 WebSocket

### Connection
```
ws://localhost:8000/ws/realtime
```

### Message Types

**Sensor Data:**
```json
{
  "type": "sensor_data",
  "device_id": "TEMP-001",
  "device_name": "Freezer Principal",
  "value": -17.5,
  "unit": "°C",
  "quality": 1.0,
  "timestamp": "2025-01-17T03:30:00Z"
}
```

**Alert:**
```json
{
  "type": "alert",
  "severity": "critical",
  "title": "Temperatura Alta",
  "alert_message": "Temperatura excede límite"
}
```

**Device Status:**
```json
{
  "type": "device_status",
  "device_id": "TEMP-001",
  "status": "online"
}
```

**Heartbeat:**
```json
{
  "type": "heartbeat",
  "timestamp": "2025-01-17T03:30:00Z"
}
```

---

## 📝 Error Responses

### 400 Bad Request
```json
{
  "detail": "Device with this ID already exists"
}
```

### 404 Not Found
```json
{
  "detail": "Device not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 🧪 Example Requests

### cURL

**Get Devices:**
```bash
curl http://localhost:8000/api/devices
```

**Create Device:**
```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "TEMP-002",
    "name": "New Sensor",
    "device_type": "temperature"
  }'
```

**Get Sensor Data:**
```bash
curl "http://localhost:8000/api/data/TEMP-001?hours=24&limit=100"
```

### Python

```python
import requests

# Get devices
response = requests.get('http://localhost:8000/api/devices')
devices = response.json()

# Post sensor data
data = {
    'device_id': 'TEMP-001',
    'value': 22.5,
    'unit': '°C'
}
response = requests.post('http://localhost:8000/api/data', json=data)
```

### JavaScript

```javascript
// Fetch devices
fetch('http://localhost:8000/api/devices')
  .then(res => res.json())
  .then(devices => console.log(devices));

// Create device
fetch('http://localhost:8000/api/devices', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    device_id: 'TEMP-002',
    name: 'New Sensor',
    device_type: 'temperature'
  })
});
```

---

## 🔐 Future: Authentication

In production, use JWT tokens:

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=admin123"

# Response
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}

# Authenticated request
curl http://localhost:8000/api/devices \
  -H "Authorization: Bearer eyJhbGc..."
```

---

## 📚 Interactive API Docs

FastAPI provides automatic interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-17

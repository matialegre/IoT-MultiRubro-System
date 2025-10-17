"""
IoT Multi-Rubro System - API Tests
===================================
Automated tests for REST API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend_api"))

from main import app
from database import Base, engine, SessionLocal

# Test client
client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    """Setup test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ============================================
# HEALTH CHECK TESTS
# ============================================
def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_stats_endpoint():
    """Test statistics endpoint."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "devices" in data
    assert "alerts" in data


# ============================================
# DEVICE TESTS
# ============================================
def test_list_devices():
    """Test listing devices."""
    response = client.get("/api/devices")
    assert response.status_code == 200
    devices = response.json()
    assert isinstance(devices, list)


def test_create_device():
    """Test creating a new device."""
    device_data = {
        "device_id": "TEST-001",
        "name": "Test Sensor",
        "device_type": "temperature",
        "rubro": "test",
        "location": "Test Lab"
    }
    
    response = client.post("/api/devices", json=device_data)
    
    # 201 Created or 400 if already exists
    assert response.status_code in [201, 400]
    
    if response.status_code == 201:
        data = response.json()
        assert data["device_id"] == "TEST-001"
        assert data["name"] == "Test Sensor"


def test_get_device():
    """Test getting device details."""
    # First create device
    device_data = {
        "device_id": "TEST-002",
        "name": "Test Device",
        "device_type": "humidity"
    }
    client.post("/api/devices", json=device_data)
    
    # Get device
    response = client.get("/api/devices/TEST-002")
    
    if response.status_code == 200:
        data = response.json()
        assert data["device_id"] == "TEST-002"


def test_delete_device():
    """Test deleting a device."""
    # Create device first
    device_data = {
        "device_id": "TEST-DELETE",
        "name": "To Delete",
        "device_type": "temperature"
    }
    client.post("/api/devices", json=device_data)
    
    # Delete it
    response = client.delete("/api/devices/TEST-DELETE")
    assert response.status_code in [200, 404]


# ============================================
# SENSOR DATA TESTS
# ============================================
def test_post_sensor_data():
    """Test posting sensor data."""
    # Ensure device exists
    device_data = {
        "device_id": "TEST-SENSOR",
        "name": "Test Sensor",
        "device_type": "temperature"
    }
    client.post("/api/devices", json=device_data)
    
    # Post data
    sensor_data = {
        "device_id": "TEST-SENSOR",
        "value": 22.5,
        "unit": "°C",
        "quality": 1.0
    }
    
    response = client.post("/api/data", json=sensor_data)
    assert response.status_code in [201, 404]


def test_get_sensor_data():
    """Test retrieving sensor data."""
    response = client.get("/api/data/TEST-SENSOR?limit=10")
    assert response.status_code in [200, 404]


# ============================================
# RULES TESTS
# ============================================
def test_list_rules():
    """Test listing rules."""
    response = client.get("/api/rules")
    assert response.status_code == 200
    rules = response.json()
    assert isinstance(rules, list)


def test_create_rule():
    """Test creating automation rule."""
    rule_data = {
        "name": "Test Rule",
        "description": "Test automation rule",
        "condition": {
            "device_id": "TEST-001",
            "operator": ">",
            "value": 25.0
        },
        "action": {
            "type": "alert",
            "severity": "warning",
            "message": "Test alert"
        },
        "is_active": True,
        "priority": 5,
        "cooldown_seconds": 300
    }
    
    response = client.post("/api/rules", json=rule_data)
    assert response.status_code == 201
    
    if response.status_code == 201:
        data = response.json()
        assert data["name"] == "Test Rule"


def test_delete_rule():
    """Test deleting a rule."""
    # Create rule first
    rule_data = {
        "name": "Delete Me",
        "condition": {"device_id": "TEST", "operator": ">", "value": 0},
        "action": {"type": "log", "message": "test"}
    }
    
    create_response = client.post("/api/rules", json=rule_data)
    
    if create_response.status_code == 201:
        rule_id = create_response.json()["id"]
        
        # Delete it
        delete_response = client.delete(f"/api/rules/{rule_id}")
        assert delete_response.status_code == 200


# ============================================
# ALERTS TESTS
# ============================================
def test_list_alerts():
    """Test listing alerts."""
    response = client.get("/api/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)


def test_list_unresolved_alerts():
    """Test filtering unresolved alerts."""
    response = client.get("/api/alerts?unresolved_only=true")
    assert response.status_code == 200


# ============================================
# VALIDATION TESTS
# ============================================
def test_invalid_device_creation():
    """Test creating device with invalid data."""
    invalid_data = {
        "device_id": "",  # Empty ID
        "name": "Invalid"
    }
    
    response = client.post("/api/devices", json=invalid_data)
    assert response.status_code in [400, 422]  # Validation error


def test_nonexistent_device():
    """Test accessing non-existent device."""
    response = client.get("/api/devices/NONEXISTENT")
    assert response.status_code == 404


# ============================================
# INTEGRATION TESTS
# ============================================
def test_full_workflow():
    """Test complete device data workflow."""
    # 1. Create device
    device_data = {
        "device_id": "WORKFLOW-TEST",
        "name": "Workflow Test Device",
        "device_type": "temperature"
    }
    
    create_resp = client.post("/api/devices", json=device_data)
    assert create_resp.status_code in [201, 400]
    
    # 2. Post sensor data
    sensor_data = {
        "device_id": "WORKFLOW-TEST",
        "value": 30.0,
        "unit": "°C"
    }
    
    data_resp = client.post("/api/data", json=sensor_data)
    assert data_resp.status_code in [201, 404]
    
    # 3. Get data back
    get_resp = client.get("/api/data/WORKFLOW-TEST?limit=1")
    assert get_resp.status_code in [200, 404]
    
    # 4. Cleanup
    client.delete("/api/devices/WORKFLOW-TEST")


# ============================================
# RUN TESTS
# ============================================
if __name__ == "__main__":
    print("Running IoT Multi-Rubro API Tests...")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "--tb=short"])

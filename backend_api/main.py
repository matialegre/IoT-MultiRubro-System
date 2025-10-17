"""
IoT Multi-Rubro System - Main FastAPI Application
==================================================
RESTful API server with WebSocket support for real-time data streaming.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import asyncio
import json
from loguru import logger

# Local imports
import config
from database import (
    get_db, init_database, seed_demo_data,
    Device, SensorData, Rule, Alert, User,
    DeviceStatus, AlertSeverity
)
from services.rules_engine import RulesEngine

# Import API routers
try:
    from api.analytics import router as analytics_router
except ImportError:
    analytics_router = None

try:
    from api.reports import router as reports_router
except ImportError:
    reports_router = None

try:
    from api.crm import router as crm_router
except ImportError:
    crm_router = None

# Configure logging
logger.add(
    config.LOG_FILE,
    rotation=f"{config.LOG_MAX_BYTES} bytes",
    retention=config.LOG_BACKUP_COUNT,
    level=config.LOG_LEVEL
)

# ============================================
# PYDANTIC MODELS (Request/Response)
# ============================================
class DeviceCreate(BaseModel):
    device_id: str
    name: str
    device_type: str
    rubro: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class DeviceResponse(BaseModel):
    id: int
    device_id: str
    name: str
    device_type: str
    status: str
    last_seen: Optional[datetime]
    is_simulated: bool
    
    class Config:
        from_attributes = True


class SensorDataCreate(BaseModel):
    device_id: str
    value: float
    unit: Optional[str] = None
    quality: float = 1.0


class SensorDataResponse(BaseModel):
    id: int
    device_id: int
    timestamp: datetime
    value: float
    unit: Optional[str]
    quality: float
    
    class Config:
        from_attributes = True


class RuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    condition: Dict[str, Any]
    action: Dict[str, Any]
    is_active: bool = True
    priority: int = 0
    cooldown_seconds: int = 300


class RuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    condition: Dict[str, Any]
    action: Dict[str, Any]
    is_active: bool
    priority: int
    last_triggered: Optional[datetime]
    trigger_count: int
    
    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: int
    device_id: int
    severity: str
    title: str
    message: Optional[str]
    is_acknowledged: bool
    is_resolved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================
# FASTAPI APPLICATION
# ============================================
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS + ["*"],  # Allow all in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
if analytics_router:
    app.include_router(analytics_router, prefix="/api", tags=["analytics"])
    logger.info("Analytics router registered")

if reports_router:
    app.include_router(reports_router, prefix="/api", tags=["reports"])
    logger.info("Reports router registered")

if crm_router:
    app.include_router(crm_router, prefix="/api", tags=["crm"])
    logger.info("CRM router registered")

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()


# ============================================
# STARTUP & SHUTDOWN EVENTS
# ============================================
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    config.print_startup_info()
    init_database()
    seed_demo_data()
    
    # Start background tasks
    if config.SIM_MODE:
        asyncio.create_task(simulation_loop())
    
    logger.info("System started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("System shutting down")


# ============================================
# ROOT & HEALTH CHECK
# ============================================
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve frontend dashboard."""
    return FileResponse("../web_frontend/index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "mode": "simulation" if config.SIM_MODE else "hardware",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================
# DEVICE ENDPOINTS
# ============================================
@app.get("/api/devices", response_model=List[DeviceResponse])
async def list_devices(
    rubro: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all devices with optional filters."""
    query = db.query(Device)
    
    if rubro:
        query = query.filter(Device.rubro == rubro)
    if status:
        query = query.filter(Device.status == status)
    
    devices = query.all()
    return devices


@app.post("/api/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """Register a new device."""
    # Check if device already exists
    existing = db.query(Device).filter(Device.device_id == device.device_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this ID already exists"
        )
    
    db_device = Device(
        device_id=device.device_id,
        name=device.name,
        device_type=device.device_type,
        rubro=device.rubro,
        location=device.location,
        description=device.description,
        config=device.config,
        is_simulated=config.SIM_MODE,
        status=DeviceStatus.ONLINE,
        owner_id=1  # Default to first user (demo)
    )
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    logger.info(f"Device created: {device.device_id}")
    return db_device


@app.get("/api/devices/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db: Session = Depends(get_db)):
    """Get device details."""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@app.delete("/api/devices/{device_id}")
async def delete_device(device_id: str, db: Session = Depends(get_db)):
    """Delete a device."""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(device)
    db.commit()
    
    logger.info(f"Device deleted: {device_id}")
    return {"message": "Device deleted successfully"}


# ============================================
# SENSOR DATA ENDPOINTS
# ============================================
@app.get("/api/data/{device_id}")
async def get_sensor_data(
    device_id: str,
    limit: int = 100,
    hours: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get historical sensor data."""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    query = db.query(SensorData).filter(SensorData.device_id == device.id)
    
    if hours:
        since = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(SensorData.timestamp >= since)
    
    data = query.order_by(SensorData.timestamp.desc()).limit(limit).all()
    
    return {
        "device_id": device_id,
        "device_name": device.name,
        "device_type": device.device_type,
        "count": len(data),
        "data": [
            {
                "timestamp": d.timestamp.isoformat(),
                "value": d.value,
                "unit": d.unit,
                "quality": d.quality
            }
            for d in reversed(data)  # Return in chronological order
        ]
    }


@app.post("/api/data", status_code=status.HTTP_201_CREATED)
async def post_sensor_data(data: SensorDataCreate, db: Session = Depends(get_db)):
    """Manually post sensor data (for testing or external integration)."""
    device = db.query(Device).filter(Device.device_id == data.device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Create data point
    db_data = SensorData(
        device_id=device.id,
        value=data.value,
        unit=data.unit,
        quality=data.quality
    )
    
    db.add(db_data)
    
    # Update device status
    device.last_seen = datetime.utcnow()
    device.status = DeviceStatus.ONLINE
    
    db.commit()
    
    # Evaluate rules
    rules_engine = RulesEngine(db)
    actions = rules_engine.evaluate_all_rules(data.device_id, data.value)
    
    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "sensor_data",
        "device_id": data.device_id,
        "value": data.value,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {
        "message": "Data received",
        "actions_triggered": len(actions),
        "actions": actions
    }


# ============================================
# RULES ENDPOINTS
# ============================================
@app.get("/api/rules", response_model=List[RuleResponse])
async def list_rules(active_only: bool = False, db: Session = Depends(get_db)):
    """List all automation rules."""
    query = db.query(Rule)
    
    if active_only:
        query = query.filter(Rule.is_active == True)
    
    rules = query.order_by(Rule.priority.desc()).all()
    return rules


@app.post("/api/rules", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    """Create a new automation rule."""
    db_rule = Rule(
        name=rule.name,
        description=rule.description,
        condition=rule.condition,
        action=rule.action,
        is_active=rule.is_active,
        priority=rule.priority,
        cooldown_seconds=rule.cooldown_seconds
    )
    
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    logger.info(f"Rule created: {rule.name}")
    return db_rule


@app.put("/api/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(rule_id: int, rule: RuleCreate, db: Session = Depends(get_db)):
    """Update an existing rule."""
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db_rule.name = rule.name
    db_rule.description = rule.description
    db_rule.condition = rule.condition
    db_rule.action = rule.action
    db_rule.is_active = rule.is_active
    db_rule.priority = rule.priority
    db_rule.cooldown_seconds = rule.cooldown_seconds
    db_rule.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_rule)
    
    logger.info(f"Rule updated: {rule.name}")
    return db_rule


@app.delete("/api/rules/{rule_id}")
async def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a rule."""
    db_rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(db_rule)
    db.commit()
    
    return {"message": "Rule deleted successfully"}


# ============================================
# ALERTS ENDPOINTS
# ============================================
@app.get("/api/alerts", response_model=List[AlertResponse])
async def list_alerts(
    unresolved_only: bool = False,
    severity: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List system alerts."""
    query = db.query(Alert)
    
    if unresolved_only:
        query = query.filter(Alert.is_resolved == False)
    
    if severity:
        query = query.filter(Alert.severity == severity)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return alerts


@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Acknowledge an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Alert acknowledged"}


@app.post("/api/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Resolve an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Alert resolved"}


# ============================================
# STATISTICS ENDPOINT
# ============================================
@app.get("/api/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get system statistics."""
    total_devices = db.query(Device).count()
    online_devices = db.query(Device).filter(Device.status == DeviceStatus.ONLINE).count()
    total_alerts = db.query(Alert).filter(Alert.is_resolved == False).count()
    critical_alerts = db.query(Alert).filter(
        Alert.is_resolved == False,
        Alert.severity == AlertSeverity.CRITICAL
    ).count()
    
    # Data points in last 24h
    since_24h = datetime.utcnow() - timedelta(hours=24)
    datapoints_24h = db.query(SensorData).filter(SensorData.timestamp >= since_24h).count()
    
    return {
        "devices": {
            "total": total_devices,
            "online": online_devices,
            "offline": total_devices - online_devices
        },
        "alerts": {
            "total": total_alerts,
            "critical": critical_alerts
        },
        "data": {
            "points_24h": datapoints_24h,
            "rate_per_minute": round(datapoints_24h / (24 * 60), 2)
        },
        "system": {
            "mode": "simulation" if config.SIM_MODE else "hardware",
            "uptime": "N/A"  # TODO: Calculate from startup time
        }
    }


# ============================================
# WEBSOCKET ENDPOINT
# ============================================
@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data streaming."""
    await manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive with heartbeat
            await asyncio.sleep(config.WS_HEARTBEAT_INTERVAL)
            await websocket.send_json({"type": "heartbeat", "timestamp": datetime.utcnow().isoformat()})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================
# SIMULATION LOOP (Background Task)
# ============================================
async def simulation_loop():
    """Background task that generates simulated sensor data."""
    logger.info("Starting simulation loop...")
    
    # Import simulator
    import sys
    sys.path.append("../simulator")
    from sensor_models import create_sensor
    
    # Create simulated sensors
    sensors = {}
    
    await asyncio.sleep(5)  # Wait for DB to initialize
    
    while True:
        try:
            # Get database session
            db = next(get_db())
            
            # Get all simulated devices
            devices = db.query(Device).filter(Device.is_simulated == True).all()
            
            for device in devices:
                # Create sensor model if not exists
                if device.device_id not in sensors:
                    try:
                        sensors[device.device_id] = create_sensor(
                            device.device_type,
                            device.device_id,
                            **(device.config or {})
                        )
                        logger.info(f"Created simulator for {device.device_id}")
                    except Exception as e:
                        logger.error(f"Error creating sensor {device.device_id}: {e}")
                        continue
                
                # Read sensor value
                sensor = sensors[device.device_id]
                state = sensor.read()
                
                # Save to database
                data_point = SensorData(
                    device_id=device.id,
                    value=state.value,
                    unit=config.get_sensor_config(device.device_type).get("unit", ""),
                    quality=state.quality
                )
                
                db.add(data_point)
                device.last_seen = datetime.utcnow()
                device.status = DeviceStatus.ONLINE if state.is_connected else DeviceStatus.OFFLINE
                
                # Evaluate rules
                if state.is_connected:
                    rules_engine = RulesEngine(db)
                    rules_engine.evaluate_all_rules(device.device_id, state.value)
                
                # Broadcast to WebSocket
                await manager.broadcast({
                    "type": "sensor_data",
                    "device_id": device.device_id,
                    "device_name": device.name,
                    "value": round(state.value, 2),
                    "unit": config.get_sensor_config(device.device_type).get("unit", ""),
                    "quality": state.quality,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            db.commit()
            db.close()
            
            # Wait before next iteration
            await asyncio.sleep(config.SIMULATOR_UPDATE_RATE)
        
        except Exception as e:
            logger.error(f"Error in simulation loop: {e}")
            await asyncio.sleep(5)


# ============================================
# RUN SERVER
# ============================================
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.SIM_MODE,
        log_level="info"
    )

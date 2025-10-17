"""
Database Models and Connection Management
==========================================
SQLAlchemy ORM models for the IoT Multi-Rubro System.
Supports both SQLite (simulation) and SQL Server (production).
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional, Dict, Any
import enum

from config import DATABASE_URL

# ============================================
# DATABASE SETUP
# ============================================
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================
# ENUMS
# ============================================
class DeviceStatus(str, enum.Enum):
    """Device connection status."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RuleAction(str, enum.Enum):
    """Actions for automation rules."""
    ALERT = "alert"
    ACTUATE = "actuate"
    NOTIFY = "notify"
    LOG = "log"


# ============================================
# ORM MODELS
# ============================================
class User(Base):
    """System users with role-based access."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # admin, user, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    devices = relationship("Device", back_populates="owner")


class Device(Base):
    """IoT devices (sensors, actuators, ESP32 nodes)."""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)  # temperature, humidity, etc.
    rubro = Column(String(50))  # carniceria, bar, riego, etc.
    location = Column(String(100))
    description = Column(Text)
    
    # Network information
    ip_address = Column(String(15))
    mac_address = Column(String(17))
    firmware_version = Column(String(20))
    
    # Status
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.OFFLINE)
    last_seen = Column(DateTime)
    is_simulated = Column(Boolean, default=True)
    
    # Configuration
    config = Column(JSON)  # Device-specific configuration
    calibration = Column(JSON)  # Calibration parameters
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="devices")
    data_points = relationship("SensorData", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")


class SensorData(Base):
    """Time-series sensor readings."""
    __tablename__ = "sensor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Measurement
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    quality = Column(Float, default=1.0)  # 0-1 signal quality
    
    # Metadata
    is_anomaly = Column(Boolean, default=False)
    metadata = Column(JSON)  # Additional context
    
    # Relationships
    device = relationship("Device", back_populates="data_points")


class Rule(Base):
    """Automation rules (if-then logic)."""
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Condition (JSON format)
    # Example: {"sensor": "TEMP-001", "operator": ">", "value": 25}
    condition = Column(JSON, nullable=False)
    
    # Action (JSON format)
    # Example: {"type": "alert", "severity": "warning", "message": "High temp"}
    action = Column(JSON, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher = more important
    
    # Execution tracking
    last_triggered = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    cooldown_seconds = Column(Integer, default=300)  # 5 minutes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    """System alerts and notifications."""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), index=True)
    rule_id = Column(Integer, ForeignKey("rules.id"))
    
    # Alert details
    severity = Column(SQLEnum(AlertSeverity), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text)
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    resolved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    device = relationship("Device", back_populates="alerts")


class Appointment(Base):
    """Appointments for medical/aesthetic centers."""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(100), nullable=False)
    client_phone = Column(String(20))
    client_email = Column(String(100))
    
    # Appointment details
    service_type = Column(String(100))
    scheduled_at = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=30)
    
    # Status
    status = Column(String(20), default="scheduled")  # scheduled, confirmed, completed, cancelled
    reminder_sent = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RFIDCard(Base):
    """RFID/QR cards for bar/nightclub system."""
    __tablename__ = "rfid_cards"
    
    id = Column(Integer, primary_key=True, index=True)
    card_number = Column(String(50), unique=True, nullable=False, index=True)
    card_type = Column(String(20), default="cliente")  # cliente, staff, vip
    
    # Card holder
    holder_name = Column(String(100))
    holder_phone = Column(String(20))
    
    # Balance
    balance = Column(Float, default=0.0)
    total_loaded = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)


class Transaction(Base):
    """Financial transactions for bar/nightclub."""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    card_id = Column(Integer, ForeignKey("rfid_cards.id"), index=True)
    
    # Transaction details
    transaction_type = Column(String(20), nullable=False)  # load, purchase, refund
    amount = Column(Float, nullable=False)
    description = Column(String(200))
    
    # Balance snapshot
    balance_before = Column(Float)
    balance_after = Column(Float)
    
    # Metadata
    pos_terminal = Column(String(50))
    operator = Column(String(100))
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class SystemLog(Base):
    """System event logs."""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    module = Column(String(50))
    message = Column(Text, nullable=False)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# ============================================
# DATABASE UTILITIES
# ============================================
def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def seed_demo_data():
    """Seed database with demo data for testing."""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Demo data already exists, skipping seed")
            return
        
        # Create demo user
        demo_user = User(
            username="admin",
            email="admin@iot-multirubro.local",
            hashed_password=pwd_context.hash("admin123"),
            full_name="System Administrator",
            role="admin"
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        
        # Create demo devices
        devices = [
            Device(
                device_id="TEMP-001",
                name="Freezer Principal",
                device_type="temperature",
                rubro="carniceria",
                location="Sala de Refrigeración",
                status=DeviceStatus.ONLINE,
                is_simulated=True,
                config={"min_temp": -18, "max_temp": -15},
                owner_id=demo_user.id
            ),
            Device(
                device_id="HUM-001",
                name="Sensor Humedad",
                device_type="humidity",
                rubro="carniceria",
                location="Sala de Refrigeración",
                status=DeviceStatus.ONLINE,
                is_simulated=True,
                owner_id=demo_user.id
            ),
            Device(
                device_id="MOT-001",
                name="Contador de Personas",
                device_type="motion",
                rubro="tienda_ropa",
                location="Entrada Principal",
                status=DeviceStatus.ONLINE,
                is_simulated=True,
                owner_id=demo_user.id
            ),
            Device(
                device_id="SOIL-001",
                name="Sensor Humedad Suelo",
                device_type="soil_moisture",
                rubro="riego",
                location="Zona A",
                status=DeviceStatus.ONLINE,
                is_simulated=True,
                owner_id=demo_user.id
            ),
        ]
        
        for device in devices:
            db.add(device)
        
        db.commit()
        
        # Create demo rules
        rules = [
            Rule(
                name="Alerta Temperatura Alta",
                description="Alertar si temperatura supera -10°C",
                condition={
                    "device_id": "TEMP-001",
                    "parameter": "value",
                    "operator": ">",
                    "value": -10
                },
                action={
                    "type": "alert",
                    "severity": "critical",
                    "message": "Temperatura del freezer demasiado alta!"
                },
                is_active=True,
                priority=10
            ),
            Rule(
                name="Riego Automático",
                description="Activar riego si humedad < 30%",
                condition={
                    "device_id": "SOIL-001",
                    "parameter": "value",
                    "operator": "<",
                    "value": 30
                },
                action={
                    "type": "actuate",
                    "target": "VALVE-001",
                    "command": "open"
                },
                is_active=True,
                priority=5
            ),
        ]
        
        for rule in rules:
            db.add(rule)
        
        db.commit()
        print("✓ Demo data seeded successfully")
        
    except Exception as e:
        print(f"✗ Error seeding demo data: {e}")
        db.rollback()
    finally:
        db.close()


# ============================================
# INITIALIZE ON IMPORT
# ============================================
if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    seed_demo_data()
    print("\n✓ Database ready!")

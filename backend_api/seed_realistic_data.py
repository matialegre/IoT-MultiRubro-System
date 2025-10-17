#!/usr/bin/env python3
"""
IoT Multi-Rubro - Realistic Data Seeding
=========================================
Populates database with realistic demo data for all rubros.
"""

import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, init_database
from database import Device, SensorData, Rule, Alert, User
from database import Appointment, RFIDCard, Transaction, SystemLog
from sqlalchemy.exc import IntegrityError

def seed_realistic_data():
    """Seed database with realistic data for all rubros."""
    
    print("🌱 Seeding realistic data...")
    
    # Initialize database
    init_database()
    
    db = SessionLocal()
    
    try:
        # Create admin user
        create_users(db)
        
        # Seed data by rubro
        print("\n📦 Seeding Carnicería/Panadería data...")
        seed_carniceria(db)
        
        print("\n🌱 Seeding Riego/Agricultura data...")
        seed_riego(db)
        
        print("\n👕 Seeding Tienda de Ropa data...")
        seed_tienda_ropa(db)
        
        print("\n🍺 Seeding Bar/Boliche data...")
        seed_bar_boliche(db)
        
        print("\n🏥 Seeding Centro Médico data...")
        seed_centro_medico(db)
        
        print("\n✅ Realistic data seeding completed!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

# ============================================
# USERS
# ============================================
def create_users(db):
    """Create system users."""
    users_data = [
        {
            "username": "admin",
            "email": "admin@iot-multirubro.local",
            "full_name": "Administrador Sistema",
            "role": "admin",
            "hashed_password": "hashed_admin123"  # In production, use proper hashing
        },
        {
            "username": "operador",
            "email": "operador@iot-multirubro.local",
            "full_name": "Operador de Planta",
            "role": "operator",
            "hashed_password": "hashed_operator123"
        },
        {
            "username": "supervisor",
            "email": "supervisor@iot-multirubro.local",
            "full_name": "Supervisor de Área",
            "role": "supervisor",
            "hashed_password": "hashed_supervisor123"
        }
    ]
    
    for user_data in users_data:
        try:
            user = User(**user_data)
            db.add(user)
            db.commit()
            print(f"  ✓ User created: {user.username}")
        except IntegrityError:
            db.rollback()
            print(f"  ⚠ User already exists: {user_data['username']}")

# ============================================
# CARNICERÍA / PANADERÍA
# ============================================
def seed_carniceria(db):
    """Seed carnicería/panadería data."""
    
    # Devices
    devices = [
        {
            "device_id": "CARN-TEMP-001",
            "name": "Freezer Principal",
            "device_type": "temperature",
            "rubro": "carniceria",
            "location": "Cámara Frigorífica A",
            "description": "Sensor temperatura principal del freezer",
            "is_simulated": True,
            "config": {"min_temp": -20, "max_temp": -15, "alert_threshold": -10}
        },
        {
            "device_id": "CARN-TEMP-002",
            "name": "Heladera Carnes Frescas",
            "device_type": "temperature",
            "rubro": "carniceria",
            "location": "Sala de Ventas",
            "description": "Heladera de exhibición",
            "is_simulated": True,
            "config": {"min_temp": 0, "max_temp": 4, "alert_threshold": 6}
        },
        {
            "device_id": "CARN-TEMP-003",
            "name": "Cámara de Maduración",
            "device_type": "temperature",
            "rubro": "carniceria",
            "location": "Cámara Maduración",
            "description": "Control temperatura maduración de carnes",
            "is_simulated": True,
            "config": {"min_temp": -2, "max_temp": 2, "alert_threshold": 4}
        },
        {
            "device_id": "CARN-HUM-001",
            "name": "Sensor Humedad Cámara",
            "device_type": "humidity",
            "rubro": "carniceria",
            "location": "Cámara Frigorífica A",
            "description": "Control humedad para evitar congelamiento",
            "is_simulated": True,
            "config": {"min_hum": 70, "max_hum": 80}
        },
        {
            "device_id": "CARN-DOOR-001",
            "name": "Sensor Puerta Cámara",
            "device_type": "motion",
            "rubro": "carniceria",
            "location": "Puerta Cámara A",
            "description": "Detecta apertura de puerta",
            "is_simulated": True
        }
    ]
    
    created_devices = []
    for device_data in devices:
        try:
            device = Device(**device_data)
            db.add(device)
            db.commit()
            db.refresh(device)
            created_devices.append(device)
            print(f"  ✓ Device: {device.name}")
        except IntegrityError:
            db.rollback()
            # Get existing device
            device = db.query(Device).filter_by(device_id=device_data["device_id"]).first()
            if device:
                created_devices.append(device)
    
    # Generate historical sensor data (last 7 days)
    now = datetime.utcnow()
    
    for device in created_devices:
        if device.device_type == "temperature":
            # Generate temperature data
            base_temp = -18 if "Freezer" in device.name else 2
            for days_ago in range(7, 0, -1):
                for hour in range(24):
                    timestamp = now - timedelta(days=days_ago, hours=hour)
                    
                    # Add daily variation
                    variation = random.uniform(-1.5, 1.5)
                    
                    # Add event simulation (door opening)
                    if random.random() < 0.05:  # 5% chance
                        variation += random.uniform(2, 5)  # Temperature spike
                    
                    value = base_temp + variation
                    
                    sensor_data = SensorData(
                        device_id=device.id,
                        value=value,
                        unit="°C",
                        quality=random.uniform(0.95, 1.0),
                        metadata={"simulated": True},
                        timestamp=timestamp
                    )
                    db.add(sensor_data)
            
            print(f"    ↳ Generated 168 temperature readings for {device.name}")
        
        elif device.device_type == "humidity":
            # Generate humidity data
            for days_ago in range(7, 0, -1):
                for hour in range(24):
                    timestamp = now - timedelta(days=days_ago, hours=hour)
                    value = random.uniform(72, 78)
                    
                    sensor_data = SensorData(
                        device_id=device.id,
                        value=value,
                        unit="%",
                        quality=random.uniform(0.95, 1.0),
                        timestamp=timestamp
                    )
                    db.add(sensor_data)
            
            print(f"    ↳ Generated 168 humidity readings")
    
    db.commit()
    
    # Create rules
    rules = [
        {
            "name": "Alerta Temperatura Alta Freezer",
            "description": "Temperatura del freezer supera -10°C",
            "condition": {
                "device_id": "CARN-TEMP-001",
                "operator": ">",
                "value": -10.0,
                "parameter": "value"
            },
            "action": {
                "type": "alert",
                "severity": "critical",
                "message": "⚠️ CRÍTICO: Temperatura freezer fuera de rango ({value}°C)"
            },
            "is_active": True,
            "priority": 10,
            "cooldown_seconds": 300
        },
        {
            "name": "Advertencia Temperatura Subiendo",
            "description": "Temperatura acercándose al límite",
            "condition": {
                "device_id": "CARN-TEMP-001",
                "operator": ">",
                "value": -14.0
            },
            "action": {
                "type": "alert",
                "severity": "warning",
                "message": "⚠️ Temperatura del freezer subiendo: {value}°C"
            },
            "is_active": True,
            "priority": 5,
            "cooldown_seconds": 600
        },
        {
            "name": "Humedad Excesiva",
            "description": "Humedad alta puede causar escarcha",
            "condition": {
                "device_id": "CARN-HUM-001",
                "operator": ">",
                "value": 85.0
            },
            "action": {
                "type": "alert",
                "severity": "warning",
                "message": "Humedad alta en cámara: {value}%"
            },
            "is_active": True,
            "priority": 3
        }
    ]
    
    for rule_data in rules:
        try:
            rule = Rule(**rule_data)
            db.add(rule)
            db.commit()
            print(f"  ✓ Rule: {rule.name}")
        except IntegrityError:
            db.rollback()
    
    # Create some historical alerts
    create_sample_alerts(db, created_devices[0], "Temperatura alta detectada", "warning", 3)

# ============================================
# RIEGO / AGRICULTURA
# ============================================
def seed_riego(db):
    """Seed irrigation system data."""
    
    devices = [
        {
            "device_id": "RIEGO-SOIL-A01",
            "name": "Sensor Humedad Zona A",
            "device_type": "soil_moisture",
            "rubro": "riego",
            "location": "Huerta Zona A",
            "description": "Sensor humedad suelo zona hortalizas",
            "is_simulated": True,
            "config": {"min_moisture": 30, "optimal": 50, "max_moisture": 70}
        },
        {
            "device_id": "RIEGO-SOIL-B01",
            "name": "Sensor Humedad Zona B",
            "device_type": "soil_moisture",
            "rubro": "riego",
            "location": "Huerta Zona B",
            "description": "Sensor humedad suelo zona frutales",
            "is_simulated": True,
            "config": {"min_moisture": 25, "optimal": 45, "max_moisture": 65}
        },
        {
            "device_id": "RIEGO-TEMP-001",
            "name": "Temperatura Ambiente",
            "device_type": "temperature",
            "rubro": "riego",
            "location": "Exterior",
            "description": "Sensor temperatura ambiente",
            "is_simulated": True
        },
        {
            "device_id": "RIEGO-FLOW-001",
            "name": "Caudalímetro Principal",
            "device_type": "flow",
            "rubro": "riego",
            "location": "Tubería Principal",
            "description": "Medidor de flujo de agua",
            "is_simulated": True,
            "config": {"max_flow": 100}
        }
    ]
    
    created_devices = []
    for device_data in devices:
        try:
            device = Device(**device_data)
            db.add(device)
            db.commit()
            db.refresh(device)
            created_devices.append(device)
            print(f"  ✓ Device: {device.name}")
        except IntegrityError:
            db.rollback()
            device = db.query(Device).filter_by(device_id=device_data["device_id"]).first()
            if device:
                created_devices.append(device)
    
    # Generate sensor data
    now = datetime.utcnow()
    
    for device in created_devices:
        if device.device_type == "soil_moisture":
            # Simulate irrigation cycles
            moisture = 45.0
            for days_ago in range(7, 0, -1):
                for hour in range(24):
                    timestamp = now - timedelta(days=days_ago, hours=hour)
                    
                    # Evaporation during day
                    if 6 <= hour <= 18:
                        moisture -= random.uniform(0.5, 1.5)
                    else:
                        moisture -= random.uniform(0.1, 0.3)
                    
                    # Irrigation at 6 AM and 6 PM
                    if hour in [6, 18]:
                        moisture = min(moisture + random.uniform(15, 25), 70)
                    
                    moisture = max(20, min(moisture, 75))
                    
                    sensor_data = SensorData(
                        device_id=device.id,
                        value=moisture,
                        unit="%",
                        quality=random.uniform(0.9, 1.0),
                        timestamp=timestamp
                    )
                    db.add(sensor_data)
            
            print(f"    ↳ Generated irrigation data for {device.name}")
        
        elif device.device_type == "temperature":
            # Daily temperature cycle
            for days_ago in range(7, 0, -1):
                for hour in range(24):
                    timestamp = now - timedelta(days=days_ago, hours=hour)
                    
                    # Simulate day/night cycle
                    base_temp = 22
                    daily_variation = 8 * ((hour - 12) / 12)  # Peak at noon
                    value = base_temp + daily_variation + random.uniform(-2, 2)
                    
                    sensor_data = SensorData(
                        device_id=device.id,
                        value=value,
                        unit="°C",
                        quality=random.uniform(0.95, 1.0),
                        timestamp=timestamp
                    )
                    db.add(sensor_data)
    
    db.commit()
    
    # Rules for irrigation
    rules = [
        {
            "name": "Riego Automático Zona A",
            "description": "Activar riego cuando humedad baja",
            "condition": {
                "device_id": "RIEGO-SOIL-A01",
                "operator": "<",
                "value": 30.0
            },
            "action": {
                "type": "actuate",
                "target": "VALVE-A01",
                "command": "open",
                "duration": 1800
            },
            "is_active": True,
            "priority": 8
        },
        {
            "name": "Riego Automático Zona B",
            "description": "Activar riego cuando humedad baja",
            "condition": {
                "device_id": "RIEGO-SOIL-B01",
                "operator": "<",
                "value": 25.0
            },
            "action": {
                "type": "actuate",
                "target": "VALVE-B01",
                "command": "open"
            },
            "is_active": True,
            "priority": 8
        }
    ]
    
    for rule_data in rules:
        try:
            rule = Rule(**rule_data)
            db.add(rule)
            db.commit()
            print(f"  ✓ Rule: {rule.name}")
        except IntegrityError:
            db.rollback()

# ============================================
# TIENDA DE ROPA
# ============================================
def seed_tienda_ropa(db):
    """Seed clothing store data."""
    
    devices = [
        {
            "device_id": "TIENDA-MOT-001",
            "name": "Contador Personas Entrada",
            "device_type": "motion",
            "rubro": "tienda_ropa",
            "location": "Puerta Principal",
            "description": "Contador de visitantes",
            "is_simulated": True
        },
        {
            "device_id": "TIENDA-LUX-001",
            "name": "Sensor Luminosidad",
            "device_type": "luminosity",
            "rubro": "tienda_ropa",
            "location": "Sala Principal",
            "description": "Control automático de iluminación",
            "is_simulated": True
        }
    ]
    
    created_devices = []
    for device_data in devices:
        try:
            device = Device(**device_data)
            db.add(device)
            db.commit()
            db.refresh(device)
            created_devices.append(device)
            print(f"  ✓ Device: {device.name}")
        except IntegrityError:
            db.rollback()
            device = db.query(Device).filter_by(device_id=device_data["device_id"]).first()
            if device:
                created_devices.append(device)
    
    # Generate people counter data
    now = datetime.utcnow()
    
    for device in created_devices:
        if device.device_type == "motion":
            # Realistic foot traffic by hour
            for days_ago in range(7, 0, -1):
                for hour in range(10, 22):  # Store hours 10 AM - 10 PM
                    timestamp = now - timedelta(days=days_ago, hours=hour)
                    
                    # More traffic on weekends and peak hours
                    is_weekend = (now - timedelta(days=days_ago)).weekday() >= 5
                    is_peak = hour in [12, 13, 14, 18, 19, 20]
                    
                    base_visitors = 15 if is_weekend else 10
                    if is_peak:
                        base_visitors *= 2
                    
                    visitors = random.randint(base_visitors - 5, base_visitors + 10)
                    
                    sensor_data = SensorData(
                        device_id=device.id,
                        value=float(visitors),
                        unit="persons",
                        quality=1.0,
                        timestamp=timestamp,
                        metadata={"cumulative": False}
                    )
                    db.add(sensor_data)
            
            print(f"    ↳ Generated foot traffic data")
    
    db.commit()

# ============================================
# BAR / BOLICHE
# ============================================
def seed_bar_boliche(db):
    """Seed bar/nightclub RFID system data."""
    
    # Create RFID cards
    card_types = [
        ("cliente", 50),
        ("vip", 10),
        ("staff", 5)
    ]
    
    created_cards = []
    card_number = 1000
    
    for card_type, count in card_types:
        for _ in range(count):
            try:
                card = RFIDCard(
                    card_number=f"CARD-{card_number:06d}",
                    card_type=card_type,
                    holder_name=f"Usuario {card_number}",
                    balance=random.uniform(500, 5000) if card_type == "cliente" else 0,
                    is_active=random.random() > 0.1  # 90% active
                )
                db.add(card)
                db.commit()
                db.refresh(card)
                created_cards.append(card)
                card_number += 1
            except IntegrityError:
                db.rollback()
        
        print(f"  ✓ Created {count} {card_type} cards")
    
    # Generate transaction history (last 30 days)
    now = datetime.utcnow()
    
    products = [
        ("Cerveza", 350),
        ("Fernet", 450),
        ("Gaseosa", 200),
        ("Vodka", 500),
        ("Whisky", 800),
        ("Energizante", 300),
        ("Agua", 150)
    ]
    
    transaction_count = 0
    for days_ago in range(30, 0, -1):
        # More transactions on weekends
        is_weekend = (now - timedelta(days=days_ago)).weekday() >= 5
        daily_transactions = random.randint(100, 150) if is_weekend else random.randint(30, 60)
        
        for _ in range(daily_transactions):
            card = random.choice([c for c in created_cards if c.is_active])
            product_name, price = random.choice(products)
            
            # Random hour between 20:00 and 4:00
            hour = random.randint(20, 28) % 24
            minute = random.randint(0, 59)
            timestamp = now - timedelta(days=days_ago) + timedelta(hours=hour, minutes=minute)
            
            try:
                transaction = Transaction(
                    card_id=card.id,
                    transaction_type="purchase",
                    amount=price,
                    description=product_name,
                    timestamp=timestamp
                )
                db.add(transaction)
                transaction_count += 1
            except:
                pass
    
    db.commit()
    print(f"  ✓ Generated {transaction_count} transactions")

# ============================================
# CENTRO MÉDICO
# ============================================
def seed_centro_medico(db):
    """Seed medical center appointments."""
    
    services = [
        ("Consulta General", 60),
        ("Odontología", 45),
        ("Kinesiología", 50),
        ("Nutrición", 40),
        ("Psicología", 60),
        ("Cardiología", 45)
    ]
    
    # Generate appointments (next 30 days)
    now = datetime.utcnow()
    appointment_count = 0
    
    for days_ahead in range(0, 30):
        # 10-15 appointments per day
        daily_appointments = random.randint(10, 15)
        
        for _ in range(daily_appointments):
            service_name, duration = random.choice(services)
            
            # Working hours 8 AM - 6 PM
            hour = random.randint(8, 17)
            minute = random.choice([0, 30])
            
            appointment_time = now + timedelta(days=days_ahead, hours=hour, minutes=minute)
            
            try:
                appointment = Appointment(
                    patient_name=f"Paciente {random.randint(1000, 9999)}",
                    patient_phone=f"+54911{random.randint(10000000, 99999999)}",
                    service_type=service_name,
                    appointment_datetime=appointment_time,
                    duration_minutes=duration,
                    status=random.choice(["confirmed", "pending", "cancelled"]) if days_ahead > 0 else "confirmed",
                    notes="Turno generado automáticamente"
                )
                db.add(appointment)
                appointment_count += 1
            except:
                pass
    
    db.commit()
    print(f"  ✓ Generated {appointment_count} appointments")

# ============================================
# HELPER FUNCTIONS
# ============================================
def create_sample_alerts(db, device, message, severity, count):
    """Create sample alerts."""
    now = datetime.utcnow()
    
    for i in range(count):
        timestamp = now - timedelta(hours=random.randint(1, 48))
        
        alert = Alert(
            device_id=device.id,
            rule_id=None,
            severity=severity,
            title=f"Alerta {device.name}",
            message=message,
            is_acknowledged=random.random() > 0.5,
            is_resolved=random.random() > 0.7,
            created_at=timestamp
        )
        db.add(alert)
    
    db.commit()
    print(f"  ✓ Created {count} sample alerts")

if __name__ == "__main__":
    seed_realistic_data()

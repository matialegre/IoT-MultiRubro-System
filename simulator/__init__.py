"""
IoT Multi-Rubro - Sensor Simulator Package
===========================================
Advanced physics-based sensor simulation.
"""

from .sensor_models import (
    BaseSensorModel,
    TemperatureSensor,
    HumiditySensor,
    WeightSensor,
    FlowSensor,
    MotionSensor,
    LuminositySensor,
    SoilMoistureSensor,
    DistanceSensor,
    create_sensor,
    SENSOR_MODELS,
)

__version__ = "1.0.0"
__all__ = [
    "BaseSensorModel",
    "TemperatureSensor",
    "HumiditySensor",
    "WeightSensor",
    "FlowSensor",
    "MotionSensor",
    "LuminositySensor",
    "SoilMoistureSensor",
    "DistanceSensor",
    "create_sensor",
    "SENSOR_MODELS",
]

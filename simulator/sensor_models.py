"""
Advanced Sensor Simulation Models
==================================
Physics-based models for realistic sensor data generation.
Each sensor type includes noise, drift, and failure modes.
"""

import numpy as np
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import math


@dataclass
class SensorState:
    """Current state of a sensor."""
    value: float
    timestamp: float
    quality: float = 1.0  # 0-1, where 1 is perfect
    is_connected: bool = True
    last_error: Optional[str] = None


class BaseSensorModel(ABC):
    """Base class for all sensor models."""
    
    def __init__(
        self,
        sensor_id: str,
        noise_level: float = 0.05,
        drift_rate: float = 0.001,
        failure_probability: float = 0.0001
    ):
        self.sensor_id = sensor_id
        self.noise_level = noise_level
        self.drift_rate = drift_rate
        self.failure_probability = failure_probability
        self.drift_offset = 0.0
        self.is_failed = False
        self.start_time = time.time()
        self.state = SensorState(value=0.0, timestamp=time.time())
        
    @abstractmethod
    def _compute_base_value(self, t: float) -> float:
        """Compute base sensor value at time t."""
        pass
    
    def _add_noise(self, value: float) -> float:
        """Add white noise to sensor reading."""
        noise = np.random.normal(0, self.noise_level * abs(value))
        return value + noise
    
    def _update_drift(self, dt: float):
        """Update sensor drift over time."""
        self.drift_offset += np.random.normal(0, self.drift_rate) * dt
    
    def _check_failure(self) -> bool:
        """Randomly simulate sensor failure."""
        if np.random.random() < self.failure_probability:
            self.is_failed = True
            return True
        return False
    
    def read(self) -> SensorState:
        """Read current sensor value."""
        current_time = time.time()
        dt = current_time - self.state.timestamp
        
        # Check for failure
        if not self.is_failed:
            self._check_failure()
        
        if self.is_failed:
            self.state.is_connected = False
            self.state.quality = 0.0
            self.state.last_error = "Sensor failure"
            return self.state
        
        # Update drift
        self._update_drift(dt)
        
        # Compute base value
        t = current_time - self.start_time
        base_value = self._compute_base_value(t)
        
        # Add noise and drift
        noisy_value = self._add_noise(base_value) + self.drift_offset
        
        # Update state
        self.state.value = noisy_value
        self.state.timestamp = current_time
        self.state.quality = np.clip(1.0 - abs(self.drift_offset) / 10.0, 0.0, 1.0)
        self.state.is_connected = True
        self.state.last_error = None
        
        return self.state
    
    def reset(self):
        """Reset sensor to initial state."""
        self.is_failed = False
        self.drift_offset = 0.0
        self.start_time = time.time()


class TemperatureSensor(BaseSensorModel):
    """
    Temperature sensor with daily cycle and thermal inertia.
    Models realistic temperature variations with sinusoidal base.
    """
    
    def __init__(
        self,
        sensor_id: str,
        base_temp: float = 20.0,
        amplitude: float = 5.0,
        period: float = 86400.0,  # 24 hours
        thermal_inertia: float = 0.1,
        **kwargs
    ):
        super().__init__(sensor_id, **kwargs)
        self.base_temp = base_temp
        self.amplitude = amplitude
        self.period = period
        self.thermal_inertia = thermal_inertia
        self.last_value = base_temp
        
    def _compute_base_value(self, t: float) -> float:
        """Sinusoidal temperature variation with thermal inertia."""
        # Daily cycle
        target = self.base_temp + self.amplitude * math.sin(2 * math.pi * t / self.period)
        
        # Apply thermal inertia (exponential smoothing)
        self.last_value += (target - self.last_value) * self.thermal_inertia
        
        return self.last_value


class HumiditySensor(BaseSensorModel):
    """
    Humidity sensor correlated with temperature.
    Inverse relationship: higher temp → lower humidity.
    """
    
    def __init__(
        self,
        sensor_id: str,
        base_humidity: float = 60.0,
        temp_correlation: float = -0.5,
        temp_sensor: Optional[TemperatureSensor] = None,
        **kwargs
    ):
        super().__init__(sensor_id, **kwargs)
        self.base_humidity = base_humidity
        self.temp_correlation = temp_correlation
        self.temp_sensor = temp_sensor
        
    def _compute_base_value(self, t: float) -> float:
        """Humidity inversely correlated with temperature."""
        humidity = self.base_humidity
        
        # If temperature sensor available, correlate
        if self.temp_sensor:
            temp_state = self.temp_sensor.read()
            temp_delta = temp_state.value - 20.0  # Reference: 20°C
            humidity += temp_delta * self.temp_correlation
        else:
            # Random walk
            humidity += np.random.normal(0, 0.5)
        
        return np.clip(humidity, 0, 100)


class WeightSensor(BaseSensorModel):
    """
    Load cell / strain gauge sensor with offset and thermal drift.
    Models weight with hysteresis and temperature compensation.
    """
    
    def __init__(
        self,
        sensor_id: str,
        tare_weight: float = 0.0,
        max_capacity: float = 100.0,
        temp_coefficient: float = 0.002,  # 0.2% per °C
        **kwargs
    ):
        super().__init__(sensor_id, **kwargs)
        self.tare_weight = tare_weight
        self.max_capacity = max_capacity
        self.temp_coefficient = temp_coefficient
        self.true_weight = tare_weight
        
    def _compute_base_value(self, t: float) -> float:
        """Weight with thermal drift compensation."""
        # Simulate slow weight changes (loading/unloading)
        if np.random.random() < 0.01:  # 1% chance per reading
            self.true_weight += np.random.uniform(-5, 5)
            self.true_weight = np.clip(self.true_weight, 0, self.max_capacity)
        
        # Temperature-induced drift (assume room temp variations)
        temp_drift = self.true_weight * self.temp_coefficient * np.random.uniform(-2, 2)
        
        return self.true_weight + temp_drift


class FlowSensor(BaseSensorModel):
    """
    Flow meter sensor for liquids.
    Pulsed flow based on valve state.
    """
    
    def __init__(
        self,
        sensor_id: str,
        max_flow: float = 10.0,  # L/min
        valve_open: bool = False,
        pulse_noise: float = 0.1,
        **kwargs
    ):
        super().__init__(sensor_id, **kwargs)
        self.max_flow = max_flow
        self.valve_open = valve_open
        self.pulse_noise = pulse_noise
        
    def set_valve_state(self, open: bool):
        """Control valve state."""
        self.valve_open = open
        
    def _compute_base_value(self, t: float) -> float:
        """Flow based on valve state with turbulence."""
        if not self.valve_open:
            return 0.0
        
        # Turbulent flow with random pulses
        base_flow = self.max_flow * (0.9 + 0.1 * math.sin(t * 10))
        turbulence = np.random.uniform(-self.pulse_noise, self.pulse_noise) * self.max_flow
        
        return np.clip(base_flow + turbulence, 0, self.max_flow * 1.1)


class MotionSensor(BaseSensorModel):
    """
    PIR motion sensor with time-dependent activity.
    More activity during business hours.
    """
    
    def __init__(
        self,
        sensor_id: str,
        business_hours: tuple = (9, 21),  # 9 AM to 9 PM
        peak_probability: float = 0.3,
        **kwargs
    ):
        super().__init__(sensor_id, **kwargs)
        self.business_hours = business_hours
        self.peak_probability = peak_probability
        self.last_motion_time = 0
        self.motion_duration = 0
        
    def _compute_base_value(self, t: float) -> float:
        """Binary motion detection with time-based probability."""
        current_time = time.time()
        
        # Check if still in motion duration
        if current_time - self.last_motion_time < self.motion_duration:
            return 1.0
        
        # Get current hour
        from datetime import datetime
        current_hour = datetime.now().hour
        
        # Calculate probability based on time
        if self.business_hours[0] <= current_hour < self.business_hours[1]:
            probability = self.peak_probability
        else:
            probability = self.peak_probability * 0.1  # Low activity outside hours
        
        # Detect motion
        if np.random.random() < probability:
            self.last_motion_time = current_time
            self.motion_duration = np.random.uniform(2, 10)  # 2-10 seconds
            return 1.0
        
        return 0.0


class LuminositySensor(BaseSensorModel):
    """
    Light sensor with day/night cycle and artificial lighting.
    """
    
    def __init__(
        self,
        sensor_id: str,
        artificial_light: bool = False,
        artificial_lux: float = 500.0,
        **kwargs
    ):
        super().__init__(sensor_id, **kwargs)
        self.artificial_light = artificial_light
        self.artificial_lux = artificial_lux
        
    def set_artificial_light(self, enabled: bool):
        """Toggle artificial lighting."""
        self.artificial_light = enabled
        
    def _compute_base_value(self, t: float) -> float:
        """Luminosity with day/night cycle."""
        # Natural light (24-hour cycle)
        hour_of_day = (t / 3600) % 24
        
        if 6 <= hour_of_day <= 18:  # Daytime
            # Peak at noon
            natural_lux = 50000 * math.sin(math.pi * (hour_of_day - 6) / 12)
        else:  # Nighttime
            natural_lux = np.random.uniform(0, 10)  # Moonlight/streetlights
        
        # Add artificial light if enabled
        if self.artificial_light:
            total_lux = natural_lux + self.artificial_lux
        else:
            total_lux = natural_lux
        
        return max(0, total_lux)


class SoilMoistureSensor(BaseSensorModel):
    """
    Soil moisture sensor for irrigation systems.
    Decreases over time, increases with watering.
    """
    
    def __init__(
        self,
        sensor_id: str,
        initial_moisture: float = 60.0,
        evaporation_rate: float = 0.5,  # % per hour
        is_watering: bool = False,
        **kwargs
    ):
        super().__init__(sensor_id, **kwargs)
        self.moisture = initial_moisture
        self.evaporation_rate = evaporation_rate
        self.is_watering = is_watering
        self.last_update = time.time()
        
    def set_watering(self, enabled: bool):
        """Start/stop watering."""
        self.is_watering = enabled
        
    def _compute_base_value(self, t: float) -> float:
        """Moisture level with evaporation and watering."""
        current_time = time.time()
        dt_hours = (current_time - self.last_update) / 3600.0
        
        # Evaporation
        self.moisture -= self.evaporation_rate * dt_hours
        
        # Watering (increases moisture)
        if self.is_watering:
            self.moisture += 10 * dt_hours  # 10% per hour when watering
        
        # Clamp to valid range
        self.moisture = np.clip(self.moisture, 0, 100)
        
        self.last_update = current_time
        return self.moisture


class DistanceSensor(BaseSensorModel):
    """
    Ultrasonic distance sensor for people counting.
    """
    
    def __init__(
        self,
        sensor_id: str,
        max_distance: float = 400.0,  # cm
        detection_threshold: float = 100.0,
        **kwargs
    ):
        super().__init__(sensor_id, **kwargs)
        self.max_distance = max_distance
        self.detection_threshold = detection_threshold
        
    def _compute_base_value(self, t: float) -> float:
        """Distance measurement with person detection."""
        # Simulate person passing (< threshold)
        if np.random.random() < 0.05:  # 5% chance
            return np.random.uniform(20, self.detection_threshold)
        else:
            # No person detected
            return self.max_distance


# ============================================
# SENSOR FACTORY
# ============================================
SENSOR_MODELS = {
    "temperature": TemperatureSensor,
    "humidity": HumiditySensor,
    "weight": WeightSensor,
    "flow": FlowSensor,
    "motion": MotionSensor,
    "luminosity": LuminositySensor,
    "soil_moisture": SoilMoistureSensor,
    "distance": DistanceSensor,
}


def create_sensor(sensor_type: str, sensor_id: str, **kwargs) -> BaseSensorModel:
    """Factory function to create sensor instances."""
    sensor_class = SENSOR_MODELS.get(sensor_type)
    if not sensor_class:
        raise ValueError(f"Unknown sensor type: {sensor_type}")
    
    return sensor_class(sensor_id=sensor_id, **kwargs)


# ============================================
# DEMO & TESTING
# ============================================
if __name__ == "__main__":
    print("Testing Sensor Models...")
    
    # Create sensors
    temp = TemperatureSensor("TEMP-001", base_temp=-15, amplitude=2)
    humidity = HumiditySensor("HUM-001", temp_sensor=temp)
    motion = MotionSensor("MOT-001")
    
    # Simulate readings
    print("\nSimulating 10 readings:")
    for i in range(10):
        t_state = temp.read()
        h_state = humidity.read()
        m_state = motion.read()
        
        print(f"#{i+1} | Temp: {t_state.value:.2f}°C | "
              f"Humidity: {h_state.value:.1f}% | "
              f"Motion: {'YES' if m_state.value > 0.5 else 'NO'}")
        
        time.sleep(0.5)
    
    print("\n✓ Sensor models working correctly!")

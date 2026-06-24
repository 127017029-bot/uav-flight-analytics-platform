"""
UAV Telemetry Simulator - Physics-Based Engine
================================================
Generates realistic UAV telemetry data using simplified physics models
including kinematics, battery electrochemistry, motor thermodynamics,
and environmental factors. Supports multiple flight profiles, sensor
noise injection, and configurable fault scenarios.

Author: UAV Analytics Platform
"""

import math
import random
import time
import json
import requests
import argparse
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple


# ============================================================
# Data Classes
# ============================================================

@dataclass
class Vector3:
    """3D vector for position, velocity, and acceleration."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector3()
        return Vector3(self.x / mag, self.y / mag, self.z / mag)


@dataclass
class DroneState:
    """Complete state vector for a simulated drone."""
    # Position (geodetic)
    latitude: float = 10.7905      # Trichy, India
    longitude: float = 78.7047
    altitude_msl: float = 88.0     # meters above sea level
    altitude_agl: float = 0.0      # meters above ground

    # Velocity
    ground_speed: float = 0.0      # m/s
    air_speed: float = 0.0         # m/s
    vertical_speed: float = 0.0    # m/s

    # Attitude (degrees)
    heading: float = 0.0           # 0-360
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

    # Battery
    battery_voltage: float = 16.8   # 4S LiPo fully charged
    battery_current: float = 0.0    # Amps
    battery_percentage: float = 100.0
    battery_temperature: float = 25.0

    # Motors (quadcopter: 4 motors)
    motor_rpm: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    motor_temp: List[float] = field(default_factory=lambda: [25.0, 25.0, 25.0, 25.0])

    # Vibration (g)
    vibration: Vector3 = field(default_factory=Vector3)

    # GPS
    gps_satellites: int = 12
    gps_fix_type: int = 3          # 3D fix
    gps_hdop: float = 0.8

    # Signal
    signal_strength: int = 100

    # Environmental
    wind_speed: float = 0.0        # m/s
    wind_direction: float = 0.0    # degrees
    ambient_temperature: float = 28.0
    barometric_pressure: float = 1013.25  # hPa
    humidity: float = 65.0

    # Internal
    flight_time: float = 0.0       # seconds elapsed
    distance_traveled: float = 0.0  # meters


@dataclass
class FaultConfig:
    """Configuration for fault injection scenarios."""
    motor_degradation: bool = False
    motor_degradation_index: int = 0     # which motor (0-3)
    motor_degradation_rate: float = 0.01  # RPM loss per second

    battery_cell_weak: bool = False
    battery_weak_cell_factor: float = 0.85  # voltage multiplier

    gps_drift: bool = False
    gps_drift_start_time: float = 120.0     # seconds into flight
    gps_drift_magnitude: float = 0.0005     # degrees

    compass_interference: bool = False
    compass_error_deg: float = 15.0

    high_vibration: bool = False
    vibration_multiplier: float = 3.0


# ============================================================
# Physics Models
# ============================================================

class BatteryModel:
    """
    Simplified LiPo battery electrochemical model.
    Models voltage-capacity curve, load-dependent sag,
    and temperature effects.
    """

    def __init__(self, cells: int = 4, capacity_mah: int = 5000):
        self.cells = cells
        self.capacity_mah = capacity_mah
        self.capacity_remaining = capacity_mah
        self.voltage_per_cell_full = 4.2
        self.voltage_per_cell_nominal = 3.7
        self.voltage_per_cell_empty = 3.3
        self.internal_resistance_ohm = 0.015 * cells  # per-cell × cells
        self.temperature = 25.0

    def get_open_circuit_voltage(self, soc: float) -> float:
        """
        OCV as a function of state of charge (0-1).
        Uses a polynomial approximation of the LiPo discharge curve.
        """
        soc = max(0, min(1, soc))
        # Polynomial fit for LiPo OCV curve
        ocv = (
            3.3 +
            0.65 * soc +
            0.15 * math.sin(math.pi * soc) +
            0.1 * soc ** 2
        )
        return ocv * self.cells

    def update(self, current_draw: float, dt: float, ambient_temp: float = 25.0) -> dict:
        """
        Update battery state for a time step.

        Args:
            current_draw: Current draw in amps
            dt: Time step in seconds
            ambient_temp: Ambient temperature in Celsius

        Returns:
            dict with voltage, current, percentage, temperature
        """
        # Drain capacity
        drain_mah = (current_draw * dt) / 3.6  # A·s to mAh
        self.capacity_remaining -= drain_mah
        self.capacity_remaining = max(0, self.capacity_remaining)

        soc = self.capacity_remaining / self.capacity_mah

        # Open circuit voltage
        ocv = self.get_open_circuit_voltage(soc)

        # Voltage sag under load (V = OCV - I * R_internal)
        voltage_sag = current_draw * self.internal_resistance_ohm
        terminal_voltage = ocv - voltage_sag

        # Temperature model: I²R heating + ambient cooling
        heat_generated = current_draw ** 2 * self.internal_resistance_ohm * 0.001
        cooling_rate = 0.02 * (self.temperature - ambient_temp)
        self.temperature += (heat_generated - cooling_rate) * dt
        self.temperature = max(ambient_temp - 5, min(65, self.temperature))

        return {
            'voltage': round(terminal_voltage, 2),
            'current': round(current_draw, 2),
            'percentage': round(soc * 100, 1),
            'temperature': round(self.temperature, 1),
        }


class MotorModel:
    """
    Simplified BLDC motor model for a quadcopter.
    Models RPM response, thermal behavior, and vibration.
    """

    def __init__(self, kv: int = 920, max_rpm: int = 8000):
        self.kv = kv
        self.max_rpm = max_rpm
        self.current_rpm = 0
        self.temperature = 25.0
        self.wear_factor = 1.0  # 1.0 = new, decreases with wear
        self.total_runtime = 0.0

    def update(self, throttle: float, voltage: float, dt: float,
               ambient_temp: float = 25.0, wear_decrement: float = 0.0) -> dict:
        """
        Update motor state.

        Args:
            throttle: 0.0 to 1.0
            voltage: Supply voltage
            dt: Time step in seconds
            ambient_temp: Ambient temperature
            wear_decrement: Additional RPM loss from fault injection

        Returns:
            dict with rpm, temperature
        """
        # Target RPM based on throttle and voltage
        target_rpm = int(throttle * self.kv * voltage * 0.08)
        target_rpm = min(target_rpm, self.max_rpm)

        # Apply wear factor
        self.wear_factor = max(0.5, self.wear_factor - wear_decrement * dt)
        target_rpm = int(target_rpm * self.wear_factor)

        # RPM response (first-order lag)
        tau = 0.15  # time constant in seconds
        alpha = 1 - math.exp(-dt / tau)
        self.current_rpm = int(self.current_rpm + alpha * (target_rpm - self.current_rpm))

        # Thermal model
        power_dissipated = (self.current_rpm / self.max_rpm) ** 2 * 50  # watts (simplified)
        thermal_resistance = 2.5  # °C/W
        heat_gain = power_dissipated * thermal_resistance * 0.01
        heat_loss = 0.03 * (self.temperature - ambient_temp)
        self.temperature += (heat_gain - heat_loss) * dt
        self.temperature = max(ambient_temp, min(120, self.temperature))

        self.total_runtime += dt

        return {
            'rpm': self.current_rpm,
            'temperature': round(self.temperature, 1),
        }


class EnvironmentModel:
    """
    Environmental simulation: wind, temperature, pressure.
    Uses Perlin-like noise for realistic variation.
    """

    def __init__(self, base_wind: float = 3.0, base_temp: float = 28.0):
        self.base_wind_speed = base_wind
        self.base_wind_direction = random.uniform(0, 360)
        self.base_temperature = base_temp
        self.base_pressure = 1013.25
        self.base_humidity = 65.0
        self._time = 0.0

    def _smooth_noise(self, t: float, frequency: float = 0.1) -> float:
        """Generate smooth pseudo-random variation."""
        return math.sin(t * frequency) * 0.3 + math.sin(t * frequency * 2.7) * 0.2

    def update(self, dt: float, altitude: float = 0.0) -> dict:
        """Update environmental conditions."""
        self._time += dt

        # Wind: base + gusts (smooth variation)
        gust = self._smooth_noise(self._time, 0.05) * 4.0
        wind_speed = max(0, self.base_wind_speed + gust + random.gauss(0, 0.3))

        # Wind direction: slow drift
        direction_drift = self._smooth_noise(self._time, 0.02) * 20
        wind_direction = (self.base_wind_direction + direction_drift) % 360

        # Temperature: decreases with altitude (lapse rate ~6.5°C/km)
        temp = self.base_temperature - (altitude / 1000.0) * 6.5
        temp += self._smooth_noise(self._time, 0.01) * 2.0

        # Pressure: decreases with altitude (barometric formula)
        pressure = self.base_pressure * math.exp(-altitude / 8500.0)

        # Humidity: slight variation
        humidity = self.base_humidity + self._smooth_noise(self._time, 0.03) * 10

        return {
            'wind_speed': round(wind_speed, 1),
            'wind_direction': round(wind_direction, 1),
            'temperature': round(temp, 1),
            'pressure': round(pressure, 2),
            'humidity': round(max(20, min(95, humidity)), 1),
        }


class SensorNoise:
    """
    Sensor noise models for realistic telemetry.
    Each sensor type has characteristic noise profiles.
    """

    @staticmethod
    def gps_noise(lat: float, lon: float, alt: float,
                  hdop: float = 1.0) -> Tuple[float, float, float]:
        """Add GPS measurement noise. Accuracy ~2-5m CEP."""
        # Convert meter noise to degree noise (~1° lat ≈ 111km)
        meter_noise = random.gauss(0, 1.5 * hdop)
        lat_noise = meter_noise / 111000.0
        lon_noise = meter_noise / (111000.0 * math.cos(math.radians(lat)))
        alt_noise = random.gauss(0, 2.5 * hdop)
        return lat + lat_noise, lon + lon_noise, alt + alt_noise

    @staticmethod
    def imu_noise(roll: float, pitch: float, yaw: float) -> Tuple[float, float, float]:
        """Add IMU measurement noise."""
        return (
            roll + random.gauss(0, 0.3),
            pitch + random.gauss(0, 0.3),
            yaw + random.gauss(0, 0.5),
        )

    @staticmethod
    def barometer_noise(altitude: float) -> float:
        """Add barometric altitude noise."""
        return altitude + random.gauss(0, 0.5)

    @staticmethod
    def speed_noise(speed: float) -> float:
        """Add speed measurement noise."""
        return max(0, speed + random.gauss(0, 0.2))

    @staticmethod
    def vibration(base_level: float = 0.5, motor_rpm_avg: float = 5000,
                  fault_multiplier: float = 1.0) -> Vector3:
        """Generate vibration readings based on motor state."""
        rpm_factor = (motor_rpm_avg / 5000.0) ** 1.5
        noise = base_level * rpm_factor * fault_multiplier
        return Vector3(
            round(random.gauss(0, noise), 3),
            round(random.gauss(0, noise), 3),
            round(random.gauss(0, noise * 1.2), 3),  # Z-axis typically higher
        )


# ============================================================
# Flight Profiles
# ============================================================

class FlightPhase:
    """Enumeration of flight phases."""
    PREFLIGHT = 'preflight'
    TAKEOFF = 'takeoff'
    CLIMB = 'climb'
    CRUISE = 'cruise'
    SURVEY = 'survey'
    HOVER = 'hover'
    DESCEND = 'descend'
    LAND = 'land'
    COMPLETE = 'complete'


@dataclass
class Waypoint:
    """A waypoint in the flight plan."""
    latitude: float
    longitude: float
    altitude: float
    speed: float = 10.0
    hover_time: float = 0.0  # seconds to hover at waypoint
    action: str = 'flyover'


class FlightProfile:
    """Generates flight plans with different mission profiles."""

    @staticmethod
    def survey_grid(center_lat: float, center_lon: float,
                    grid_size: float = 0.002, lines: int = 5,
                    altitude: float = 50.0) -> List[Waypoint]:
        """Generate a survey grid pattern."""
        waypoints = []
        half = grid_size / 2
        spacing = grid_size / (lines - 1) if lines > 1 else grid_size

        for i in range(lines):
            lon_offset = -half + i * spacing
            if i % 2 == 0:  # Alternate direction for efficiency
                waypoints.append(Waypoint(center_lat - half, center_lon + lon_offset, altitude, 8.0))
                waypoints.append(Waypoint(center_lat + half, center_lon + lon_offset, altitude, 8.0))
            else:
                waypoints.append(Waypoint(center_lat + half, center_lon + lon_offset, altitude, 8.0))
                waypoints.append(Waypoint(center_lat - half, center_lon + lon_offset, altitude, 8.0))

        return waypoints

    @staticmethod
    def inspection_orbit(center_lat: float, center_lon: float,
                         radius: float = 0.001, points: int = 12,
                         altitude: float = 40.0) -> List[Waypoint]:
        """Generate an orbital inspection pattern around a point of interest."""
        waypoints = []
        for i in range(points + 1):
            angle = (2 * math.pi * i) / points
            lat = center_lat + radius * math.cos(angle)
            lon = center_lon + radius * math.sin(angle)
            waypoints.append(Waypoint(lat, lon, altitude, 5.0, hover_time=3.0, action='take_photo'))
        return waypoints

    @staticmethod
    def delivery_route(start_lat: float, start_lon: float,
                       dest_lat: float, dest_lon: float,
                       altitude: float = 60.0) -> List[Waypoint]:
        """Generate a point-to-point delivery route."""
        return [
            Waypoint(start_lat, start_lon, altitude, 15.0),
            Waypoint(dest_lat, dest_lon, altitude, 15.0),
            Waypoint(dest_lat, dest_lon, 10.0, 3.0, hover_time=30.0, action='hover'),
            Waypoint(start_lat, start_lon, altitude, 15.0),
        ]

    @staticmethod
    def simple_circuit(center_lat: float, center_lon: float,
                       size: float = 0.003, altitude: float = 50.0) -> List[Waypoint]:
        """Generate a simple rectangular circuit."""
        half = size / 2
        return [
            Waypoint(center_lat + half, center_lon - half, altitude, 12.0),
            Waypoint(center_lat + half, center_lon + half, altitude, 12.0),
            Waypoint(center_lat - half, center_lon + half, altitude, 12.0),
            Waypoint(center_lat - half, center_lon - half, altitude, 12.0),
        ]


# ============================================================
# Main Simulator Engine
# ============================================================

class UAVSimulator:
    """
    Physics-based UAV telemetry simulator.

    Generates realistic telemetry by simulating flight dynamics,
    battery electrochemistry, motor thermodynamics, environmental
    conditions, and sensor characteristics.
    """

    def __init__(self, drone_id: int = 1, flight_id: int = 1,
                 profile: str = 'survey', faults: Optional[FaultConfig] = None):
        self.drone_id = drone_id
        self.flight_id = flight_id
        self.profile = profile
        self.faults = faults or FaultConfig()

        # Initialize subsystem models
        self.state = DroneState()
        self.battery = BatteryModel(cells=4, capacity_mah=5000)
        self.motors = [MotorModel() for _ in range(4)]
        self.environment = EnvironmentModel()
        self.noise = SensorNoise()

        # Flight plan
        self.waypoints = self._generate_waypoints()
        self.current_waypoint_idx = 0
        self.phase = FlightPhase.PREFLIGHT
        self.hover_timer = 0.0

        # Timing
        self.dt = 0.1  # 10Hz simulation
        self.elapsed = 0.0
        self.sequence = 0

        # Home position
        self.home_lat = self.state.latitude
        self.home_lon = self.state.longitude
        self.home_alt = self.state.altitude_msl

    def _generate_waypoints(self) -> List[Waypoint]:
        """Generate waypoints based on flight profile."""
        lat, lon = self.state.latitude, self.state.longitude
        profiles = {
            'survey': lambda: FlightProfile.survey_grid(lat, lon, 0.003, 5, 50),
            'inspection': lambda: FlightProfile.inspection_orbit(lat, lon, 0.001, 12, 40),
            'delivery': lambda: FlightProfile.delivery_route(
                lat, lon, lat + 0.005, lon + 0.003, 60),
            'circuit': lambda: FlightProfile.simple_circuit(lat, lon, 0.003, 50),
        }
        generator = profiles.get(self.profile, profiles['circuit'])
        return generator()

    def _compute_heading(self, target_lat: float, target_lon: float) -> float:
        """Compute heading to target using great-circle bearing."""
        lat1 = math.radians(self.state.latitude)
        lat2 = math.radians(target_lat)
        dlon = math.radians(target_lon - self.state.longitude)

        x = math.sin(dlon) * math.cos(lat2)
        y = (math.cos(lat1) * math.sin(lat2) -
             math.sin(lat1) * math.cos(lat2) * math.cos(dlon))

        bearing = math.degrees(math.atan2(x, y))
        return bearing % 360

    def _distance_to(self, target_lat: float, target_lon: float) -> float:
        """Haversine distance in meters."""
        R = 6371000  # Earth radius in meters
        lat1, lat2 = math.radians(self.state.latitude), math.radians(target_lat)
        dlat = lat2 - lat1
        dlon = math.radians(target_lon - self.state.longitude)

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _compute_throttle(self) -> float:
        """Compute throttle based on current flight phase."""
        phase_throttle = {
            FlightPhase.PREFLIGHT: 0.0,
            FlightPhase.TAKEOFF: 0.65,
            FlightPhase.CLIMB: 0.60,
            FlightPhase.CRUISE: 0.50,
            FlightPhase.SURVEY: 0.45,
            FlightPhase.HOVER: 0.48,
            FlightPhase.DESCEND: 0.35,
            FlightPhase.LAND: 0.30,
            FlightPhase.COMPLETE: 0.0,
        }
        return phase_throttle.get(self.phase, 0.0)

    def _compute_current_draw(self, throttle: float) -> float:
        """Estimate current draw based on throttle and flight conditions."""
        # Base hover current ~15A for typical quadcopter
        hover_current = 15.0
        # Current scales roughly with throttle^1.5 (prop aerodynamics)
        base_current = hover_current * (throttle / 0.48) ** 1.5 if throttle > 0 else 0.5
        # Wind increases power demand
        wind_factor = 1.0 + (self.state.wind_speed / 20.0) * 0.15
        return base_current * wind_factor

    def _update_phase(self):
        """State machine for flight phase transitions."""
        if self.phase == FlightPhase.PREFLIGHT:
            if self.elapsed >= 5.0:  # 5 second preflight check
                self.phase = FlightPhase.TAKEOFF

        elif self.phase == FlightPhase.TAKEOFF:
            if self.state.altitude_agl >= 10.0:
                self.phase = FlightPhase.CLIMB

        elif self.phase == FlightPhase.CLIMB:
            if self.current_waypoint_idx < len(self.waypoints):
                target_alt = self.waypoints[self.current_waypoint_idx].altitude
                if self.state.altitude_agl >= target_alt - 2:
                    self.phase = FlightPhase.CRUISE
            else:
                self.phase = FlightPhase.DESCEND

        elif self.phase == FlightPhase.CRUISE:
            if self.current_waypoint_idx >= len(self.waypoints):
                self.phase = FlightPhase.DESCEND
            else:
                wp = self.waypoints[self.current_waypoint_idx]
                dist = self._distance_to(wp.latitude, wp.longitude)
                if dist < 3.0:  # Within 3m of waypoint
                    if wp.hover_time > 0:
                        self.phase = FlightPhase.HOVER
                        self.hover_timer = wp.hover_time
                    else:
                        self.current_waypoint_idx += 1

        elif self.phase == FlightPhase.HOVER:
            self.hover_timer -= self.dt
            if self.hover_timer <= 0:
                self.current_waypoint_idx += 1
                if self.current_waypoint_idx >= len(self.waypoints):
                    self.phase = FlightPhase.DESCEND
                else:
                    self.phase = FlightPhase.CRUISE

        elif self.phase == FlightPhase.DESCEND:
            if self.state.altitude_agl <= 5.0:
                self.phase = FlightPhase.LAND

        elif self.phase == FlightPhase.LAND:
            if self.state.altitude_agl <= 0.3:
                self.state.altitude_agl = 0.0
                self.phase = FlightPhase.COMPLETE

        # Emergency: low battery forces RTH
        if self.state.battery_percentage < 15 and self.phase in (
                FlightPhase.CRUISE, FlightPhase.SURVEY, FlightPhase.HOVER):
            self.phase = FlightPhase.DESCEND

    def _update_position(self):
        """Update drone position based on current phase and waypoints."""
        if self.phase == FlightPhase.PREFLIGHT or self.phase == FlightPhase.COMPLETE:
            self.state.ground_speed = 0
            self.state.vertical_speed = 0
            return

        if self.phase == FlightPhase.TAKEOFF:
            self.state.vertical_speed = 2.5  # m/s climb
            self.state.ground_speed = 0
            self.state.altitude_agl += self.state.vertical_speed * self.dt

        elif self.phase == FlightPhase.CLIMB:
            target_alt = self.waypoints[self.current_waypoint_idx].altitude if self.current_waypoint_idx < len(self.waypoints) else 50
            alt_diff = target_alt - self.state.altitude_agl
            self.state.vertical_speed = min(3.0, max(0.5, alt_diff * 0.3))
            self.state.altitude_agl += self.state.vertical_speed * self.dt
            self.state.ground_speed = 2.0

        elif self.phase in (FlightPhase.CRUISE, FlightPhase.SURVEY):
            if self.current_waypoint_idx < len(self.waypoints):
                wp = self.waypoints[self.current_waypoint_idx]
                target_heading = self._compute_heading(wp.latitude, wp.longitude)

                # Smooth heading transition
                heading_diff = (target_heading - self.state.heading + 540) % 360 - 180
                self.state.heading = (self.state.heading + heading_diff * 0.1) % 360

                # Move toward waypoint
                target_speed = wp.speed
                speed_diff = target_speed - self.state.ground_speed
                self.state.ground_speed += speed_diff * 0.05

                # Update lat/lon based on heading and speed
                distance_m = self.state.ground_speed * self.dt
                dlat = distance_m * math.cos(math.radians(self.state.heading)) / 111000.0
                dlon = distance_m * math.sin(math.radians(self.state.heading)) / (
                    111000.0 * math.cos(math.radians(self.state.latitude)))

                self.state.latitude += dlat
                self.state.longitude += dlon
                self.state.distance_traveled += distance_m

                # Maintain altitude
                alt_diff = wp.altitude - self.state.altitude_agl
                self.state.vertical_speed = alt_diff * 0.2
                self.state.altitude_agl += self.state.vertical_speed * self.dt

        elif self.phase == FlightPhase.HOVER:
            self.state.ground_speed = max(0, self.state.ground_speed * 0.9)
            self.state.vertical_speed *= 0.9

        elif self.phase == FlightPhase.DESCEND:
            # Return to home
            heading_home = self._compute_heading(self.home_lat, self.home_lon)
            dist_home = self._distance_to(self.home_lat, self.home_lon)

            if dist_home > 5.0:
                heading_diff = (heading_home - self.state.heading + 540) % 360 - 180
                self.state.heading = (self.state.heading + heading_diff * 0.1) % 360
                self.state.ground_speed = min(12.0, dist_home * 0.3)

                distance_m = self.state.ground_speed * self.dt
                dlat = distance_m * math.cos(math.radians(self.state.heading)) / 111000.0
                dlon = distance_m * math.sin(math.radians(self.state.heading)) / (
                    111000.0 * math.cos(math.radians(self.state.latitude)))
                self.state.latitude += dlat
                self.state.longitude += dlon
            else:
                self.state.ground_speed = max(0, self.state.ground_speed * 0.85)

            self.state.vertical_speed = -2.0
            self.state.altitude_agl = max(0, self.state.altitude_agl + self.state.vertical_speed * self.dt)

        elif self.phase == FlightPhase.LAND:
            self.state.vertical_speed = -0.8
            self.state.ground_speed = max(0, self.state.ground_speed * 0.9)
            self.state.altitude_agl = max(0, self.state.altitude_agl + self.state.vertical_speed * self.dt)

        # Update MSL altitude
        self.state.altitude_msl = self.home_alt + self.state.altitude_agl

        # Compute attitude from motion
        if self.state.ground_speed > 1.0:
            # Pitch forward when accelerating
            self.state.pitch = -min(15, self.state.ground_speed * 0.8)
            # Bank in turns
            if hasattr(self, '_prev_heading'):
                heading_rate = (self.state.heading - self._prev_heading + 540) % 360 - 180
                self.state.roll = max(-25, min(25, heading_rate * 2))
            self._prev_heading = self.state.heading
        else:
            self.state.pitch *= 0.9
            self.state.roll *= 0.9

        self.state.yaw = self.state.heading
        self.state.air_speed = self.state.ground_speed + self.state.wind_speed * 0.3

    def _apply_faults(self):
        """Apply configured fault scenarios."""
        if self.faults.motor_degradation and self.elapsed > 30:
            idx = self.faults.motor_degradation_index
            self.motors[idx].wear_factor -= self.faults.motor_degradation_rate * self.dt

        if self.faults.gps_drift and self.elapsed > self.faults.gps_drift_start_time:
            drift_progress = (self.elapsed - self.faults.gps_drift_start_time) / 60.0
            drift = self.faults.gps_drift_magnitude * min(1.0, drift_progress)
            self.state.latitude += random.gauss(0, drift)
            self.state.longitude += random.gauss(0, drift)
            self.state.gps_hdop = min(5.0, self.state.gps_hdop + 0.01)

        if self.faults.compass_interference and self.elapsed > 60:
            self.state.heading += random.gauss(0, self.faults.compass_error_deg * 0.1)
            self.state.heading %= 360

    def step(self) -> Optional[dict]:
        """
        Execute one simulation step (0.1s) and return telemetry data.

        Returns:
            dict of telemetry values, or None if flight is complete
        """
        if self.phase == FlightPhase.COMPLETE and self.elapsed > 10:
            return None

        self.elapsed += self.dt
        self.state.flight_time = self.elapsed

        # Update environment
        env = self.environment.update(self.dt, self.state.altitude_agl)
        self.state.wind_speed = env['wind_speed']
        self.state.wind_direction = env['wind_direction']
        self.state.ambient_temperature = env['temperature']
        self.state.barometric_pressure = env['pressure']
        self.state.humidity = env['humidity']

        # Update flight phase
        self._update_phase()

        # Update position and attitude
        self._update_position()

        # Apply faults
        self._apply_faults()

        # Compute throttle and current
        throttle = self._compute_throttle()
        current = self._compute_current_draw(throttle)

        # Update battery
        batt = self.battery.update(current, self.dt, self.state.ambient_temperature)
        self.state.battery_voltage = batt['voltage']
        self.state.battery_current = batt['current']
        self.state.battery_percentage = batt['percentage']
        self.state.battery_temperature = batt['temperature']

        # Update motors
        for i in range(4):
            wear_dec = 0.0
            if self.faults.motor_degradation and i == self.faults.motor_degradation_index:
                wear_dec = self.faults.motor_degradation_rate
            motor_state = self.motors[i].update(
                throttle, self.state.battery_voltage, self.dt,
                self.state.ambient_temperature, wear_dec)
            self.state.motor_rpm[i] = motor_state['rpm']
            self.state.motor_temp[i] = motor_state['temperature']

        # Compute vibration
        avg_rpm = sum(self.state.motor_rpm) / 4.0
        vib_mult = self.faults.vibration_multiplier if self.faults.high_vibration else 1.0
        self.state.vibration = self.noise.vibration(0.5, avg_rpm, vib_mult)

        # GPS quality
        if not self.faults.gps_drift:
            self.state.gps_satellites = random.randint(10, 14)
            self.state.gps_fix_type = 3
            self.state.gps_hdop = round(random.uniform(0.6, 1.2), 1)

        # Signal strength: decreases slightly with distance from home
        dist_home = self._distance_to(self.home_lat, self.home_lon)
        self.state.signal_strength = max(30, int(100 - dist_home * 0.015))

        # Apply sensor noise
        noisy_lat, noisy_lon, noisy_alt = self.noise.gps_noise(
            self.state.latitude, self.state.longitude,
            self.state.altitude_msl, self.state.gps_hdop)
        noisy_roll, noisy_pitch, noisy_yaw = self.noise.imu_noise(
            self.state.roll, self.state.pitch, self.state.yaw)

        # Build telemetry packet
        self.sequence += 1
        telemetry = {
            'flight': self.flight_id,
            'timestamp': (datetime.now() - timedelta(seconds=0)).isoformat(),
            'sequence_number': self.sequence,

            # Position (with noise)
            'latitude': round(noisy_lat, 7),
            'longitude': round(noisy_lon, 7),
            'altitude_msl': round(noisy_alt, 1),
            'altitude_agl': round(self.noise.barometer_noise(self.state.altitude_agl), 1),

            # Velocity
            'ground_speed': round(self.noise.speed_noise(self.state.ground_speed), 2),
            'air_speed': round(self.noise.speed_noise(self.state.air_speed), 2),
            'vertical_speed': round(self.state.vertical_speed + random.gauss(0, 0.1), 2),

            # Attitude (with noise)
            'heading': round(noisy_yaw % 360, 1),
            'roll': round(noisy_roll, 1),
            'pitch': round(noisy_pitch, 1),
            'yaw': round(noisy_yaw % 360, 1),

            # Battery
            'battery_voltage': self.state.battery_voltage,
            'battery_current': self.state.battery_current,
            'battery_percentage': self.state.battery_percentage,
            'battery_temperature': self.state.battery_temperature,

            # Motors
            'motor_rpm_1': self.state.motor_rpm[0] + random.randint(-20, 20),
            'motor_rpm_2': self.state.motor_rpm[1] + random.randint(-20, 20),
            'motor_rpm_3': self.state.motor_rpm[2] + random.randint(-20, 20),
            'motor_rpm_4': self.state.motor_rpm[3] + random.randint(-20, 20),
            'motor_temp_1': self.state.motor_temp[0],
            'motor_temp_2': self.state.motor_temp[1],
            'motor_temp_3': self.state.motor_temp[2],
            'motor_temp_4': self.state.motor_temp[3],

            # Vibration
            'vibration_x': self.state.vibration.x,
            'vibration_y': self.state.vibration.y,
            'vibration_z': self.state.vibration.z,

            # GPS
            'gps_satellites': self.state.gps_satellites,
            'gps_fix_type': self.state.gps_fix_type,
            'gps_hdop': self.state.gps_hdop,

            # Signal
            'signal_strength': self.state.signal_strength,

            # Environmental
            'wind_speed_est': self.state.wind_speed,
            'wind_direction_est': self.state.wind_direction,
            'ambient_temperature': self.state.ambient_temperature,
            'barometric_pressure': self.state.barometric_pressure,
            'humidity': self.state.humidity,
        }

        return telemetry


# ============================================================
# Runner
# ============================================================

def run_simulation(api_url: str = 'http://127.0.0.1:8000/api/telemetry/ingest/',
                   flight_id: int = 1,
                   profile: str = 'survey',
                   send_rate_hz: float = 2.0,
                   enable_faults: bool = False,
                   batch_mode: bool = False,
                   batch_size: int = 50,
                   dry_run: bool = False):
    """
    Run the UAV telemetry simulator.

    Args:
        api_url: Backend API endpoint for telemetry ingestion
        flight_id: Flight ID to associate telemetry with
        profile: Flight profile ('survey', 'inspection', 'delivery', 'circuit')
        send_rate_hz: How many telemetry packets to send per second
        enable_faults: Enable random fault injection
        batch_mode: Use batch API endpoint
        batch_size: Number of points per batch
        dry_run: Print to console instead of sending to API
    """
    # Configure faults
    faults = FaultConfig()
    if enable_faults:
        fault_type = random.choice(['motor', 'battery', 'gps', 'vibration', 'none'])
        if fault_type == 'motor':
            faults.motor_degradation = True
            faults.motor_degradation_index = random.randint(0, 3)
            faults.motor_degradation_rate = random.uniform(0.005, 0.02)
            print(f"[FAULT] Motor {faults.motor_degradation_index + 1} degradation enabled")
        elif fault_type == 'battery':
            faults.battery_cell_weak = True
            print("[FAULT] Weak battery cell enabled")
        elif fault_type == 'gps':
            faults.gps_drift = True
            faults.gps_drift_start_time = random.uniform(60, 180)
            print(f"[FAULT] GPS drift at {faults.gps_drift_start_time:.0f}s")
        elif fault_type == 'vibration':
            faults.high_vibration = True
            faults.vibration_multiplier = random.uniform(2.0, 4.0)
            print(f"[FAULT] High vibration (×{faults.vibration_multiplier:.1f})")
        else:
            print("[FAULT] No faults injected this run")

    sim = UAVSimulator(flight_id=flight_id, profile=profile, faults=faults)

    print(f"\n{'='*60}")
    print(f"  UAV Telemetry Simulator")
    print(f"  Profile: {profile} | Flight: {flight_id} | Rate: {send_rate_hz}Hz")
    print(f"  Waypoints: {len(sim.waypoints)}")
    print(f"  API: {api_url if not dry_run else 'DRY RUN (console)'}")
    print(f"{'='*60}\n")

    send_interval = 1.0 / send_rate_hz
    sim_steps_per_send = int(send_interval / sim.dt)
    batch_buffer = []
    total_sent = 0

    try:
        while True:
            # Run simulation steps
            telemetry = None
            for _ in range(sim_steps_per_send):
                telemetry = sim.step()
                if telemetry is None:
                    break

            if telemetry is None:
                print(f"\n[COMPLETE] Flight finished. Total packets: {total_sent}")
                # Send remaining batch
                if batch_mode and batch_buffer:
                    _send_batch(api_url, batch_buffer, dry_run)
                    total_sent += len(batch_buffer)
                break

            if batch_mode:
                batch_buffer.append(telemetry)
                if len(batch_buffer) >= batch_size:
                    _send_batch(api_url, batch_buffer, dry_run)
                    total_sent += len(batch_buffer)
                    batch_buffer = []
            else:
                _send_single(api_url, telemetry, dry_run)
                total_sent += 1

            # Status line
            phase = sim.phase
            alt = telemetry['altitude_agl']
            spd = telemetry['ground_speed']
            batt = telemetry['battery_percentage']
            rpm_avg = (telemetry['motor_rpm_1'] + telemetry['motor_rpm_2'] +
                       telemetry['motor_rpm_3'] + telemetry['motor_rpm_4']) / 4

            print(f"\r  [{phase:>10s}] ALT:{alt:6.1f}m  SPD:{spd:5.1f}m/s  "
                  f"BATT:{batt:5.1f}%  RPM:{rpm_avg:6.0f}  "
                  f"PKT:{total_sent:>5d}", end='', flush=True)

            time.sleep(send_interval)

    except KeyboardInterrupt:
        print(f"\n\n[ABORTED] Simulation stopped by user. Packets sent: {total_sent}")


def _send_single(api_url: str, data: dict, dry_run: bool):
    """Send a single telemetry point."""
    if dry_run:
        return
    try:
        response = requests.post(api_url, json=data, timeout=5)
        if response.status_code not in (200, 201):
            print(f"\n  [WARN] API returned {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"\n  [ERROR] {e}")


def _send_batch(api_url: str, data: list, dry_run: bool):
    """Send a batch of telemetry points."""
    if dry_run:
        return
    batch_url = api_url.replace('/ingest/', '/batch/')
    try:
        response = requests.post(batch_url, json=data, timeout=10)
        if response.status_code not in (200, 201):
            print(f"\n  [WARN] Batch API returned {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"\n  [ERROR] {e}")


def generate_historical_data(flight_id: int = 1, profile: str = 'survey',
                             enable_faults: bool = False) -> list:
    """
    Generate a complete flight's telemetry data without sending to API.
    Useful for populating the database with historical data or ML training.

    Returns:
        List of telemetry dicts
    """
    faults = FaultConfig()
    if enable_faults:
        faults.motor_degradation = True
        faults.motor_degradation_index = random.randint(0, 3)
        faults.motor_degradation_rate = random.uniform(0.005, 0.015)

    sim = UAVSimulator(flight_id=flight_id, profile=profile, faults=faults)
    data = []

    while True:
        telemetry = sim.step()
        if telemetry is None:
            break
        data.append(telemetry)

    return data


# ============================================================
# CLI Entry Point
# ============================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='UAV Telemetry Simulator - Physics-Based Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Flight Profiles:
  survey      - Grid survey pattern (agricultural/mapping)
  inspection  - Orbital inspection around a POI
  delivery    - Point-to-point delivery route
  circuit     - Simple rectangular circuit

Examples:
  python simulator.py --profile survey --flight-id 1
  python simulator.py --profile inspection --faults --dry-run
  python simulator.py --profile delivery --rate 5 --batch
        """)

    parser.add_argument('--api-url', default='http://127.0.0.1:8000/api/telemetry/ingest/',
                        help='Backend API endpoint')
    parser.add_argument('--flight-id', type=int, default=1,
                        help='Flight ID to associate telemetry with')
    parser.add_argument('--profile', choices=['survey', 'inspection', 'delivery', 'circuit'],
                        default='survey', help='Flight mission profile')
    parser.add_argument('--rate', type=float, default=2.0,
                        help='Telemetry send rate in Hz')
    parser.add_argument('--faults', action='store_true',
                        help='Enable random fault injection')
    parser.add_argument('--batch', action='store_true',
                        help='Use batch API endpoint')
    parser.add_argument('--batch-size', type=int, default=50,
                        help='Batch size when using batch mode')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print to console without sending to API')

    args = parser.parse_args()

    run_simulation(
        api_url=args.api_url,
        flight_id=args.flight_id,
        profile=args.profile,
        send_rate_hz=args.rate,
        enable_faults=args.faults,
        batch_mode=args.batch,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
    )

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Drone(models.Model):
    """UAV drone asset in the fleet."""
    TYPE_CHOICES = [
        ('quadcopter', 'Quadcopter'), ('hexacopter', 'Hexacopter'),
        ('fixed_wing', 'Fixed Wing'), ('vtol', 'VTOL'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'), ('maintenance', 'Maintenance'),
        ('offline', 'Offline'), ('retired', 'Retired'),
    ]

    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    manufacturer = models.CharField(max_length=100, default='DJI')
    drone_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='quadcopter')
    max_altitude_m = models.FloatField(default=120)
    max_speed_ms = models.FloatField(default=20)
    max_flight_time_min = models.IntegerField(default=30)
    weight_kg = models.FloatField(default=1.5)
    payload_capacity_kg = models.FloatField(default=0.5)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    total_flight_hours = models.FloatField(default=0)
    total_flights = models.IntegerField(default=0)
    firmware_version = models.CharField(max_length=50, blank=True)
    last_maintenance_date = models.DateTimeField(null=True, blank=True)
    next_maintenance_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Drone'

    def __str__(self):
        return f"{self.name} ({self.serial_number})"


class ComponentHealth(models.Model):
    """Health tracking for individual drone components."""
    COMPONENT_CHOICES = [
        ('motor_1', 'Motor 1'), ('motor_2', 'Motor 2'),
        ('motor_3', 'Motor 3'), ('motor_4', 'Motor 4'),
        ('battery', 'Battery'), ('esc', 'ESC'), ('gps', 'GPS'),
        ('imu', 'IMU'), ('compass', 'Compass'), ('camera', 'Camera'),
        ('gimbal', 'Gimbal'), ('frame', 'Frame'),
    ]
    STATUS_CHOICES = [
        ('healthy', 'Healthy'), ('warning', 'Warning'),
        ('critical', 'Critical'), ('failed', 'Failed'),
    ]

    drone = models.ForeignKey(Drone, related_name='components', on_delete=models.CASCADE)
    component_type = models.CharField(max_length=20, choices=COMPONENT_CHOICES)
    component_name = models.CharField(max_length=100)
    health_score = models.FloatField(default=100.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    cycles_count = models.IntegerField(default=0)
    total_hours = models.FloatField(default=0)
    last_inspected = models.DateTimeField(null=True, blank=True)
    predicted_rul_hours = models.FloatField(null=True, blank=True)
    degradation_rate = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='healthy')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['drone', 'component_type']
        verbose_name = 'Component Health'
        verbose_name_plural = 'Component Health Records'

    def __str__(self):
        return f"{self.drone.name} - {self.get_component_type_display()} ({self.health_score}%)"


class BatteryProfile(models.Model):
    """Battery electrochemical profile and degradation tracking."""
    CHEMISTRY_CHOICES = [
        ('lipo', 'LiPo'), ('li_ion', 'Li-Ion'), ('solid_state', 'Solid State'),
    ]

    drone = models.OneToOneField(Drone, related_name='battery_profile', on_delete=models.CASCADE)
    manufacturer = models.CharField(max_length=100, default='Unknown')
    chemistry = models.CharField(max_length=20, choices=CHEMISTRY_CHOICES, default='lipo')
    cells_count = models.IntegerField(default=4)
    design_capacity_mah = models.IntegerField(default=5000)
    current_capacity_mah = models.IntegerField(default=5000)
    voltage_nominal = models.FloatField(default=14.8)
    cycle_count = models.IntegerField(default=0)
    charge_cycles = models.IntegerField(default=0)
    state_of_health = models.FloatField(default=100.0)
    estimated_rul_cycles = models.IntegerField(null=True, blank=True)
    degradation_rate_per_cycle = models.FloatField(default=0.0)
    last_full_charge = models.DateTimeField(null=True, blank=True)
    average_temperature_c = models.FloatField(default=25.0)
    max_temperature_c = models.FloatField(default=25.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Battery Profile'

    def __str__(self):
        return f"{self.drone.name} Battery (SoH: {self.state_of_health}%)"

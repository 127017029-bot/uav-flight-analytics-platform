import uuid
from django.db import models
from django.conf import settings


class Flight(models.Model):
    """Individual flight record for a drone sortie."""
    STATUS_CHOICES = [
        ('planned', 'Planned'), ('in_progress', 'In Progress'),
        ('completed', 'Completed'), ('aborted', 'Aborted'),
        ('crashed', 'Crashed'),
    ]
    WEATHER_CHOICES = [
        ('clear', 'Clear'), ('cloudy', 'Cloudy'), ('rainy', 'Rainy'),
        ('windy', 'Windy'), ('foggy', 'Foggy'), ('snowy', 'Snowy'),
        ('stormy', 'Stormy'), ('unknown', 'Unknown'),
    ]

    drone = models.ForeignKey(
        'drones.Drone', related_name='flights', on_delete=models.CASCADE,
    )
    pilot = models.ForeignKey(
        'accounts.Pilot', related_name='flights',
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    mission = models.ForeignKey(
        'missions.Mission', related_name='flights',
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    flight_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(default=0)
    distance_km = models.FloatField(default=0)
    max_altitude_m = models.FloatField(default=0)
    avg_speed_ms = models.FloatField(default=0)
    max_speed_ms = models.FloatField(default=0)
    energy_consumed_wh = models.FloatField(default=0)
    start_battery_pct = models.FloatField(default=100)
    end_battery_pct = models.FloatField(default=0)
    weather_condition = models.CharField(
        max_length=20, choices=WEATHER_CHOICES, default='unknown',
    )
    wind_speed_ms = models.FloatField(default=0)
    temperature_c = models.FloatField(default=25)
    risk_score = models.FloatField(null=True, blank=True)
    anomaly_count = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Flight'

    def __str__(self):
        return f"{self.flight_number} - {self.drone.name}"

    def save(self, *args, **kwargs):
        """Auto-generate flight number on creation."""
        if not self.flight_number:
            self.flight_number = f"FLT-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class FlightAnalytics(models.Model):
    """Computed analytics summary for a completed flight."""
    flight = models.OneToOneField(
        Flight, related_name='analytics', on_delete=models.CASCADE,
    )
    total_distance_m = models.FloatField(default=0)
    max_altitude_m = models.FloatField(default=0)
    avg_speed_ms = models.FloatField(default=0)
    max_speed_ms = models.FloatField(default=0)
    avg_vertical_speed_ms = models.FloatField(default=0)
    energy_efficiency_m_per_wh = models.FloatField(default=0)
    flight_smoothness_score = models.FloatField(default=100)
    path_efficiency = models.FloatField(default=1.0)
    risk_score = models.FloatField(default=0)
    anomaly_count = models.IntegerField(default=0)
    battery_consumed_pct = models.FloatField(default=0)
    avg_motor_rpm = models.FloatField(default=0)
    motor_rpm_variance = models.FloatField(default=0)
    avg_vibration = models.FloatField(default=0)
    max_vibration = models.FloatField(default=0)
    gps_accuracy_avg_m = models.FloatField(default=0)
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-computed_at']
        verbose_name = 'Flight Analytics'
        verbose_name_plural = 'Flight Analytics'

    def __str__(self):
        return f"Analytics for {self.flight.flight_number}"

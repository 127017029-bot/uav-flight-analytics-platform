from django.db import models
from django.conf import settings


class Alert(models.Model):
    """System alert triggered by telemetry thresholds, AI models, or rules."""
    TYPE_CHOICES = [
        ('battery_low', 'Battery Low'), ('battery_critical', 'Battery Critical'),
        ('motor_anomaly', 'Motor Anomaly'), ('gps_loss', 'GPS Loss'),
        ('signal_loss', 'Signal Loss'), ('geofence_breach', 'Geofence Breach'),
        ('altitude_warning', 'Altitude Warning'), ('speed_warning', 'Speed Warning'),
        ('temperature_warning', 'Temperature Warning'),
        ('vibration_warning', 'Vibration Warning'),
        ('maintenance_due', 'Maintenance Due'), ('system_error', 'System Error'),
        ('ai_prediction', 'AI Prediction'),
    ]
    SEVERITY_CHOICES = [
        ('info', 'Info'), ('warning', 'Warning'),
        ('critical', 'Critical'), ('emergency', 'Emergency'),
    ]

    drone = models.ForeignKey(
        'drones.Drone', related_name='alerts', on_delete=models.CASCADE,
    )
    flight = models.ForeignKey(
        'flights.Flight', related_name='alerts',
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    alert_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='warning')
    title = models.CharField(max_length=200)
    message = models.TextField()
    ai_generated = models.BooleanField(default=False)
    model_name = models.CharField(max_length=100, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='acknowledged_alerts',
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Alert'

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title} - {self.drone.name}"

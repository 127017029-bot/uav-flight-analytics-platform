from django.db import models
from django.conf import settings


class MaintenanceRecord(models.Model):
    """Maintenance work order for a drone — scheduled, predictive, or corrective."""
    TYPE_CHOICES = [
        ('scheduled', 'Scheduled'), ('predictive', 'Predictive'),
        ('corrective', 'Corrective'), ('emergency', 'Emergency'),
    ]
    COMPONENT_CHOICES = [
        ('motor_1', 'Motor 1'), ('motor_2', 'Motor 2'),
        ('motor_3', 'Motor 3'), ('motor_4', 'Motor 4'),
        ('battery', 'Battery'), ('esc', 'ESC'), ('gps', 'GPS'),
        ('imu', 'IMU'), ('compass', 'Compass'), ('camera', 'Camera'),
        ('gimbal', 'Gimbal'), ('frame', 'Frame'),
        ('full_system', 'Full System'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'), ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'), ('medium', 'Medium'),
        ('high', 'High'), ('critical', 'Critical'),
    ]

    drone = models.ForeignKey(
        'drones.Drone', related_name='maintenance_records',
        on_delete=models.CASCADE,
    )
    maintenance_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='scheduled')
    component = models.CharField(max_length=20, choices=COMPONENT_CHOICES, default='full_system')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    predicted_failure_date = models.DateTimeField(null=True, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    technician_notes = models.TextField(blank=True)
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    parts_replaced = models.TextField(blank=True, help_text='Comma-separated list of replaced parts')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='maintenance_records',
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Maintenance Record'

    def __str__(self):
        return f"{self.title} - {self.drone.name} ({self.get_status_display()})"

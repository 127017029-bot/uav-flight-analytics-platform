from django.db import models
from django.conf import settings


class Mission(models.Model):
    """Planned or executed drone mission definition."""
    TYPE_CHOICES = [
        ('survey', 'Survey'), ('inspection', 'Inspection'),
        ('delivery', 'Delivery'), ('surveillance', 'Surveillance'),
        ('mapping', 'Mapping'), ('photography', 'Photography'),
        ('custom', 'Custom'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'), ('medium', 'Medium'),
        ('high', 'High'), ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('planned', 'Planned'),
        ('in_progress', 'In Progress'), ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    mission_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='survey')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    assigned_drone = models.ForeignKey(
        'drones.Drone', related_name='missions',
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    assigned_pilot = models.ForeignKey(
        'accounts.Pilot', related_name='missions',
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    planned_start = models.DateTimeField(null=True, blank=True)
    planned_end = models.DateTimeField(null=True, blank=True)
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    estimated_distance_km = models.FloatField(default=0)
    estimated_duration_min = models.FloatField(default=0)
    estimated_battery_usage = models.FloatField(default=0)
    risk_score = models.FloatField(null=True, blank=True)
    area_of_operation = models.TextField(blank=True, help_text='Description or GeoJSON of the operational area')
    max_altitude_m = models.FloatField(default=120)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='created_missions',
        on_delete=models.SET_NULL, null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Mission'

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class Waypoint(models.Model):
    """Ordered waypoint within a mission flight plan."""
    ACTION_CHOICES = [
        ('flyover', 'Fly Over'), ('hover', 'Hover'),
        ('take_photo', 'Take Photo'), ('start_video', 'Start Video'),
        ('stop_video', 'Stop Video'), ('land', 'Land'),
        ('return_home', 'Return Home'),
    ]

    mission = models.ForeignKey(
        Mission, related_name='waypoints', on_delete=models.CASCADE,
    )
    sequence_order = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude_m = models.FloatField(default=50)
    speed_ms = models.FloatField(default=10)
    hover_time_s = models.FloatField(default=0)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, default='flyover')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['mission', 'sequence_order']
        unique_together = ['mission', 'sequence_order']
        verbose_name = 'Waypoint'

    def __str__(self):
        return f"WP{self.sequence_order} - Mission {self.mission.name}"

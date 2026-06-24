from django.db import models


class FleetDailyStats(models.Model):
    """Aggregated daily fleet-wide statistics for trend analysis.

    One record per day, computed by a background task or management command.
    """
    date = models.DateField(unique=True)
    total_flights = models.IntegerField(default=0)
    total_flight_hours = models.FloatField(default=0)
    total_distance_km = models.FloatField(default=0)
    active_drones = models.IntegerField(default=0)
    avg_fleet_health = models.FloatField(default=100)
    total_anomalies = models.IntegerField(default=0)
    total_alerts = models.IntegerField(default=0)
    energy_consumed_wh = models.FloatField(default=0)
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Fleet Daily Stats'
        verbose_name_plural = 'Fleet Daily Stats'

    def __str__(self):
        return f"Fleet Stats - {self.date}"

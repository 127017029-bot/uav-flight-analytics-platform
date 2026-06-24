from django.contrib import admin
from .models import FleetDailyStats


@admin.register(FleetDailyStats)
class FleetDailyStatsAdmin(admin.ModelAdmin):
    """Admin configuration for FleetDailyStats records."""
    list_display = [
        'date', 'total_flights', 'total_flight_hours',
        'active_drones', 'avg_fleet_health', 'total_anomalies',
        'total_alerts', 'computed_at',
    ]
    list_filter = ['date']
    date_hierarchy = 'date'

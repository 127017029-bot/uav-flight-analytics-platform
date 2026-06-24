from django.contrib import admin
from .models import Flight, FlightAnalytics


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    """Admin configuration for Flight records."""
    list_display = [
        'flight_number', 'drone', 'status', 'start_time',
        'duration_seconds', 'distance_km', 'anomaly_count',
    ]
    list_filter = ['status', 'weather_condition', 'drone']
    search_fields = ['flight_number', 'notes']
    readonly_fields = ['flight_number']


@admin.register(FlightAnalytics)
class FlightAnalyticsAdmin(admin.ModelAdmin):
    """Admin configuration for FlightAnalytics records."""
    list_display = [
        'flight', 'total_distance_m', 'max_altitude_m',
        'risk_score', 'anomaly_count', 'computed_at',
    ]
    list_filter = ['computed_at']

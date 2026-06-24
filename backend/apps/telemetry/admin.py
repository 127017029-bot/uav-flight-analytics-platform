from django.contrib import admin
from .models import TelemetryData


@admin.register(TelemetryData)
class TelemetryDataAdmin(admin.ModelAdmin):
    """Admin configuration for TelemetryData records."""
    list_display = [
        'id', 'flight', 'timestamp', 'sequence_number',
        'latitude', 'longitude', 'altitude_msl',
        'ground_speed', 'battery_percentage', 'is_anomaly',
    ]
    list_filter = ['is_anomaly', 'flight']
    search_fields = ['flight__flight_number']
    date_hierarchy = 'timestamp'

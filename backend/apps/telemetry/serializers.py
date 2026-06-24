from rest_framework import serializers
from .models import TelemetryData


class TelemetrySerializer(serializers.ModelSerializer):
    """Full serializer for telemetry data — all fields."""

    class Meta:
        model = TelemetryData
        fields = '__all__'


class TelemetryCreateSerializer(serializers.ModelSerializer):
    """Serializer for ingesting new telemetry data points.

    Accepts the minimal required fields plus any optional sensor data.
    """

    class Meta:
        model = TelemetryData
        fields = '__all__'
        read_only_fields = ['created_at']


class TelemetryCompactSerializer(serializers.ModelSerializer):
    """Compact serializer for map / list views — key fields only."""

    class Meta:
        model = TelemetryData
        fields = [
            'id', 'timestamp', 'latitude', 'longitude',
            'altitude_msl', 'ground_speed', 'battery_percentage',
            'is_anomaly',
        ]

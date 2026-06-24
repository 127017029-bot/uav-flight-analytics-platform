from rest_framework import serializers
from .models import Flight, FlightAnalytics


class FlightAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for computed flight analytics."""

    class Meta:
        model = FlightAnalytics
        fields = '__all__'


class FlightSerializer(serializers.ModelSerializer):
    """List serializer for flights — flat representation."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    weather_display = serializers.CharField(source='get_weather_condition_display', read_only=True)
    drone_name = serializers.CharField(source='drone.name', read_only=True)

    class Meta:
        model = Flight
        fields = '__all__'
        read_only_fields = ['flight_number']


class FlightDetailSerializer(serializers.ModelSerializer):
    """Detail serializer with nested analytics."""
    analytics = FlightAnalyticsSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    weather_display = serializers.CharField(source='get_weather_condition_display', read_only=True)
    drone_name = serializers.CharField(source='drone.name', read_only=True)

    class Meta:
        model = Flight
        fields = '__all__'
        read_only_fields = ['flight_number']

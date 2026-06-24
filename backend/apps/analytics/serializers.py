from rest_framework import serializers
from .models import FleetDailyStats


class FleetDailyStatsSerializer(serializers.ModelSerializer):
    """Serializer for daily fleet statistics."""

    class Meta:
        model = FleetDailyStats
        fields = '__all__'

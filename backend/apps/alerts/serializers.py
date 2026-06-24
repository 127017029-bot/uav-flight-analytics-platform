from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for system alerts."""
    type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    drone_name = serializers.CharField(source='drone.name', read_only=True)

    class Meta:
        model = Alert
        fields = '__all__'

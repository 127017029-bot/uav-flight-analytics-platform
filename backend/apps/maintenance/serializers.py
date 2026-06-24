from rest_framework import serializers
from .models import MaintenanceRecord


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for maintenance work orders."""
    type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    component_display = serializers.CharField(source='get_component_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    drone_name = serializers.CharField(source='drone.name', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = '__all__'

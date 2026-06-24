from rest_framework import serializers
from .models import Drone, ComponentHealth, BatteryProfile


class ComponentHealthSerializer(serializers.ModelSerializer):
    """Serializer for individual drone component health records."""
    component_type_display = serializers.CharField(source='get_component_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ComponentHealth
        fields = '__all__'


class BatteryProfileSerializer(serializers.ModelSerializer):
    """Serializer for battery electrochemical profile."""
    chemistry_display = serializers.CharField(source='get_chemistry_display', read_only=True)

    class Meta:
        model = BatteryProfile
        fields = '__all__'


class DroneSerializer(serializers.ModelSerializer):
    """List serializer for drones — flat representation."""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_drone_type_display', read_only=True)

    class Meta:
        model = Drone
        fields = '__all__'


class DroneDetailSerializer(serializers.ModelSerializer):
    """Detail serializer with nested components and battery profile."""
    components = ComponentHealthSerializer(many=True, read_only=True)
    battery_profile = BatteryProfileSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_drone_type_display', read_only=True)

    class Meta:
        model = Drone
        fields = '__all__'

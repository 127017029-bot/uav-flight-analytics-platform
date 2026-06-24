from rest_framework import serializers
from .models import Mission, Waypoint


class WaypointSerializer(serializers.ModelSerializer):
    """Serializer for mission waypoints."""
    action_type_display = serializers.CharField(
        source='get_action_type_display', read_only=True,
    )

    class Meta:
        model = Waypoint
        fields = '__all__'


class MissionSerializer(serializers.ModelSerializer):
    """List serializer for missions — flat representation."""
    type_display = serializers.CharField(source='get_mission_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Mission
        fields = '__all__'


class MissionDetailSerializer(serializers.ModelSerializer):
    """Detail serializer with nested waypoints."""
    waypoints = WaypointSerializer(many=True, read_only=True)
    type_display = serializers.CharField(source='get_mission_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Mission
        fields = '__all__'

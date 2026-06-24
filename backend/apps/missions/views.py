from rest_framework import viewsets, generics, permissions
from .models import Mission, Waypoint
from .serializers import MissionSerializer, MissionDetailSerializer, WaypointSerializer


class MissionViewSet(viewsets.ModelViewSet):
    """CRUD operations for mission planning and management."""
    queryset = Mission.objects.select_related(
        'assigned_drone', 'assigned_pilot', 'created_by',
    ).all()
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['status', 'mission_type', 'priority', 'assigned_drone']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'planned_start', 'priority']

    def get_serializer_class(self):
        """Return detail serializer with waypoints for retrieve action."""
        if self.action == 'retrieve':
            return MissionDetailSerializer
        return MissionSerializer


class WaypointViewSet(viewsets.ModelViewSet):
    """CRUD operations for mission waypoints."""
    serializer_class = WaypointSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        """Filter waypoints by mission if mission_id is in the URL."""
        queryset = Waypoint.objects.all()
        mission_id = self.kwargs.get('mission_pk')
        if mission_id:
            queryset = queryset.filter(mission_id=mission_id)
        return queryset

from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Sum, Count, Q
from .models import Drone, ComponentHealth, BatteryProfile
from .serializers import (
    DroneSerializer, DroneDetailSerializer,
    ComponentHealthSerializer, BatteryProfileSerializer,
)


class DroneViewSet(viewsets.ModelViewSet):
    """CRUD operations for drone fleet management."""
    queryset = Drone.objects.all()
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['status', 'drone_type', 'manufacturer']
    search_fields = ['name', 'serial_number', 'model']
    ordering_fields = ['name', 'created_at', 'total_flight_hours']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DroneDetailSerializer
        return DroneSerializer


class DroneHealthView(generics.RetrieveAPIView):
    """Get full component health data for a drone."""
    queryset = Drone.objects.prefetch_related('components').all()
    serializer_class = DroneDetailSerializer
    permission_classes = [permissions.AllowAny]


class DroneBatteryView(generics.RetrieveAPIView):
    """Get battery profile for a drone."""
    queryset = BatteryProfile.objects.select_related('drone').all()
    serializer_class = BatteryProfileSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'drone_id'


class FleetOverviewView(APIView):
    """Fleet-wide statistics and KPIs."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        drones = Drone.objects.all()
        total = drones.count()
        active = drones.filter(status='active').count()
        maintenance = drones.filter(status='maintenance').count()
        offline = drones.filter(status='offline').count()
        avg_health = ComponentHealth.objects.aggregate(
            avg=Avg('health_score'))['avg'] or 100
        total_hours = drones.aggregate(
            total=Sum('total_flight_hours'))['total'] or 0
        total_flights = drones.aggregate(
            total=Sum('total_flights'))['total'] or 0
        from apps.alerts.models import Alert
        alerts_count = Alert.objects.filter(resolved=False).count()

        return Response({
            'total_drones': total,
            'active': active,
            'maintenance': maintenance,
            'offline': offline,
            'avg_fleet_health': round(avg_health, 1),
            'total_flight_hours': round(total_hours, 1),
            'total_flights': total_flights,
            'active_alerts': alerts_count,
        })


class FleetStatusView(generics.ListAPIView):
    """All drones with current status summary."""
    queryset = Drone.objects.all()
    serializer_class = DroneSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

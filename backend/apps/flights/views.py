from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Flight, FlightAnalytics
from .serializers import (
    FlightSerializer, FlightDetailSerializer, FlightAnalyticsSerializer,
)


class FlightViewSet(viewsets.ModelViewSet):
    """CRUD operations for flight records."""
    queryset = Flight.objects.select_related('drone', 'pilot', 'mission').all()
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['status', 'drone', 'weather_condition']
    search_fields = ['flight_number', 'notes']
    ordering_fields = ['created_at', 'start_time', 'duration_seconds', 'distance_km']

    def get_serializer_class(self):
        """Return detail serializer for retrieve action."""
        if self.action == 'retrieve':
            return FlightDetailSerializer
        return FlightSerializer


class FlightTelemetryView(generics.ListAPIView):
    """List telemetry data points for a specific flight.

    Returns compact telemetry records associated with the given flight id.
    """
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        from apps.telemetry.models import TelemetryData
        return TelemetryData.objects.filter(flight_id=self.kwargs['pk'])

    def get_serializer_class(self):
        from apps.telemetry.serializers import TelemetryCompactSerializer
        return TelemetryCompactSerializer


class FlightAnalyticsView(generics.RetrieveAPIView):
    """Retrieve computed analytics for a specific flight."""
    queryset = FlightAnalytics.objects.select_related('flight').all()
    serializer_class = FlightAnalyticsSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'flight_id'
    lookup_url_kwarg = 'pk'

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Avg, Max, Min, Count, Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import TelemetryData
from .serializers import (
    TelemetrySerializer, TelemetryCreateSerializer, TelemetryCompactSerializer,
)


class TelemetryIngestView(generics.CreateAPIView):
    """Ingest a single telemetry data point and broadcast to WebSockets."""
    queryset = TelemetryData.objects.all()
    serializer_class = TelemetryCreateSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()
        channel_layer = get_channel_layer()
        if channel_layer:
            drone_id = instance.flight.drone_id
            serialized_data = TelemetrySerializer(instance).data
            async_to_sync(channel_layer.group_send)(
                f'telemetry_{drone_id}',
                {
                    'type': 'telemetry_update',
                    'data': serialized_data
                }
            )


class TelemetryBatchIngestView(APIView):
    """Ingest a batch of telemetry data points and broadcast them to WebSockets.

    Expects a JSON list of telemetry objects. Returns 201 on success with
    the count of created records.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response(
                {'error': 'Expected a list of telemetry objects.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = TelemetryCreateSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()

        channel_layer = get_channel_layer()
        if channel_layer and instances:
            for instance in instances:
                drone_id = instance.flight.drone_id
                serialized_data = TelemetrySerializer(instance).data
                async_to_sync(channel_layer.group_send)(
                    f'telemetry_{drone_id}',
                    {
                        'type': 'telemetry_update',
                        'data': serialized_data
                    }
                )
        return Response(
            {'created': len(serializer.data)},
            status=status.HTTP_201_CREATED,
        )


class TelemetryListView(generics.ListAPIView):
    """List telemetry data filtered by flight_id query parameter.

    Usage: ``GET /api/telemetry/list/?flight_id=<id>``
    """
    serializer_class = TelemetryCompactSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = TelemetryData.objects.all()
        flight_id = self.request.query_params.get('flight_id')
        if flight_id:
            queryset = queryset.filter(flight_id=flight_id)
        return queryset


class TelemetryLatestView(APIView):
    """Return the latest telemetry snapshot for a given drone.

    Resolves the drone's most recent flight and returns the last data point.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, drone_id):
        latest = (
            TelemetryData.objects
            .filter(flight__drone_id=drone_id)
            .order_by('-timestamp')
            .first()
        )
        if not latest:
            return Response(
                {'detail': 'No telemetry data found for this drone.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TelemetrySerializer(latest)
        return Response(serializer.data)


class TelemetryStatsView(APIView):
    """Return aggregated telemetry statistics.

    Optionally filter by ``flight_id`` query parameter or ``drone_id`` from path.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, drone_id=None):
        queryset = TelemetryData.objects.all()
        flight_id = request.query_params.get('flight_id')
        if flight_id:
            queryset = queryset.filter(flight_id=flight_id)
        elif drone_id:
            queryset = queryset.filter(flight__drone_id=drone_id)

        stats = queryset.aggregate(
            total_points=Count('id'),
            avg_altitude=Avg('altitude_msl'),
            max_altitude=Max('altitude_msl'),
            avg_speed=Avg('ground_speed'),
            max_speed=Max('ground_speed'),
            avg_battery=Avg('battery_percentage'),
            min_battery=Min('battery_percentage'),
            avg_vibration_x=Avg('vibration_x'),
            avg_vibration_y=Avg('vibration_y'),
            avg_vibration_z=Avg('vibration_z'),
            anomaly_count=Count('id', filter=Q(is_anomaly=True)),
        )
        return Response(stats)


class TelemetryChartDataView(APIView):
    """Return time-series telemetry data for charting.

    Returns key fields sampled from the given flight for front-end charts.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, flight_id):
        queryset = (
            TelemetryData.objects
            .filter(flight_id=flight_id)
            .order_by('timestamp')
            .values(
                'timestamp', 'altitude_msl', 'ground_speed',
                'battery_percentage', 'battery_voltage',
                'motor_rpm_1', 'motor_rpm_2', 'motor_rpm_3', 'motor_rpm_4',
                'vibration_x', 'vibration_y', 'vibration_z',
                'is_anomaly', 'anomaly_score',
            )
        )
        return Response(list(queryset))


class DroneTelemetryChartDataView(APIView):
    """Return time-series telemetry data for charting based on drone's latest flight."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, drone_id):
        from apps.flights.models import Flight
        latest_flight = Flight.objects.filter(drone_id=drone_id).order_by('-created_at').first()
        if not latest_flight:
            return Response([])
        queryset = (
            TelemetryData.objects
            .filter(flight=latest_flight)
            .order_by('timestamp')
            .values(
                'timestamp', 'altitude_msl', 'ground_speed',
                'battery_percentage', 'battery_voltage',
                'motor_rpm_1', 'motor_rpm_2', 'motor_rpm_3', 'motor_rpm_4',
                'vibration_x', 'vibration_y', 'vibration_z',
                'is_anomaly', 'anomaly_score',
            )
        )
        return Response(list(queryset))

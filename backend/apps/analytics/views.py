from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Sum, Count
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import FleetDailyStats
from .serializers import FleetDailyStatsSerializer


class FleetDailyStatsView(generics.ListAPIView):
    """List daily fleet statistics with optional date filtering.

    Query params:
    - ``days``: number of past days to include (default: 30)
    """
    serializer_class = FleetDailyStatsSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        days = int(self.request.query_params.get('days', 30))
        since = timezone.now().date() - timedelta(days=days)
        return FleetDailyStats.objects.filter(date__gte=since)


class FleetTrendsView(APIView):
    """Return 7-day, 30-day, and 90-day aggregated fleet trends."""
    permission_classes = [permissions.AllowAny]

    def _get_trend(self, days: int) -> dict:
        """Aggregate fleet stats for the given number of past days."""
        since = timezone.now().date() - timedelta(days=days)
        qs = FleetDailyStats.objects.filter(date__gte=since)
        agg = qs.aggregate(
            total_flights=Sum('total_flights'),
            total_hours=Sum('total_flight_hours'),
            total_distance=Sum('total_distance_km'),
            avg_health=Avg('avg_fleet_health'),
            total_anomalies=Sum('total_anomalies'),
            total_alerts=Sum('total_alerts'),
            total_energy=Sum('energy_consumed_wh'),
        )
        return {k: (v or 0) for k, v in agg.items()}

    def get(self, request):
        return Response({
            '7d': self._get_trend(7),
            '30d': self._get_trend(30),
            '90d': self._get_trend(90),
        })


class FlightComparisonView(APIView):
    """Compare performance across two flights.

    Query params:
    - ``flight_a``: first flight ID
    - ``flight_b``: second flight ID
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from apps.flights.models import Flight, FlightAnalytics

        flight_a_id = request.query_params.get('flight_a')
        flight_b_id = request.query_params.get('flight_b')
        if not flight_a_id or not flight_b_id:
            return Response(
                {'error': 'Both flight_a and flight_b query params are required.'},
                status=400,
            )

        def _flight_data(flight_id):
            try:
                flight = Flight.objects.get(id=flight_id)
                analytics = getattr(flight, 'analytics', None)
                return {
                    'flight_number': flight.flight_number,
                    'duration_seconds': flight.duration_seconds,
                    'distance_km': flight.distance_km,
                    'max_altitude_m': flight.max_altitude_m,
                    'avg_speed_ms': flight.avg_speed_ms,
                    'energy_consumed_wh': flight.energy_consumed_wh,
                    'anomaly_count': flight.anomaly_count,
                    'risk_score': analytics.risk_score if analytics else None,
                    'flight_smoothness': analytics.flight_smoothness_score if analytics else None,
                    'path_efficiency': analytics.path_efficiency if analytics else None,
                }
            except Flight.DoesNotExist:
                return None

        data_a = _flight_data(flight_a_id)
        data_b = _flight_data(flight_b_id)
        if not data_a or not data_b:
            return Response({'error': 'One or both flights not found.'}, status=404)

        return Response({'flight_a': data_a, 'flight_b': data_b})


from django.http import HttpResponse

def prometheus_metrics_view(request):
    """Exposes real-time system and fleet metrics in a Prometheus scraping format."""
    from apps.drones.models import Drone
    from apps.flights.models import Flight
    from apps.alerts.models import Alert
    from apps.ml.models import MLModel, MLPrediction

    active_drones = Drone.objects.filter(status='active').count()
    maintenance_drones = Drone.objects.filter(status='maintenance').count()
    total_drones = Drone.objects.count()

    total_flights = Flight.objects.count()

    active_alerts = Alert.objects.filter(is_acknowledged=False).count()
    critical_alerts = Alert.objects.filter(is_acknowledged=False, severity='critical').count()

    total_models = MLModel.objects.filter(is_active=True).count()
    total_predictions = MLPrediction.objects.count()

    metrics = [
        "# HELP uav_drones_total Total registered drones in the fleet.",
        "# TYPE uav_drones_total gauge",
        f"uav_drones_total {total_drones}",
        "",
        "# HELP uav_drones_active_count Drones currently in operation.",
        "# TYPE uav_drones_active_count gauge",
        f"uav_drones_active_count {active_drones}",
        "",
        "# HELP uav_drones_maintenance_count Drones flagged for predictive maintenance.",
        "# TYPE uav_drones_maintenance_count gauge",
        f"uav_drones_maintenance_count {maintenance_drones}",
        "",
        "# HELP uav_flights_total Cumulative flights conducted.",
        "# TYPE uav_flights_total counter",
        f"uav_flights_total {total_flights}",
        "",
        "# HELP uav_alerts_active_total Active unacknowledged alerts.",
        "# TYPE uav_alerts_active_total gauge",
        f"uav_alerts_active_total {active_alerts}",
        "",
        "# HELP uav_alerts_critical_total Active critical severity issues.",
        "# TYPE uav_alerts_critical_total gauge",
        f"uav_alerts_critical_total {critical_alerts}",
        "",
        "# HELP uav_ml_models_active Active machine learning models in registry.",
        "# TYPE uav_ml_models_active gauge",
        f"uav_ml_models_active {total_models}",
        "",
        "# HELP uav_ml_predictions_total Cumulative AI inferences computed.",
        "# TYPE uav_ml_predictions_total counter",
        f"uav_ml_predictions_total {total_predictions}",
    ]

    response_text = "\n".join(metrics) + "\n"
    return HttpResponse(response_text, content_type="text/plain; version=0.0.4")

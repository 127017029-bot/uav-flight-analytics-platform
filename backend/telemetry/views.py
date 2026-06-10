from rest_framework import generics
from .models import Telemetry
from .serializers import TelemetrySerializer
from rest_framework.response import Response
from django.db.models import Avg, Max, Min
class TelemetryCreateView(generics.CreateAPIView):
    queryset = Telemetry.objects.all()
    serializer_class = TelemetrySerializer

class TelemetryListView(generics.ListAPIView):
    queryset = Telemetry.objects.all()
    serializer_class = TelemetrySerializer
class TelemetryStatsView(generics.GenericAPIView):

    def get(self, request):

        stats = Telemetry.objects.aggregate(
            avg_speed=Avg('speed'),
            max_altitude=Max('altitude'),
            min_battery=Min('battery')
        )

        stats["total_records"] = Telemetry.objects.count()

        return Response(stats)
class TelemetryChartDataView(generics.GenericAPIView):

    def get(self, request):

        telemetry = Telemetry.objects.all().order_by('timestamp')[:100]

        data = {
            "timestamps": [],
            "altitudes": [],
            "speeds": [],
            "battery": []
        }

        for row in telemetry:
            data["timestamps"].append(str(row.timestamp))
            data["altitudes"].append(row.altitude)
            data["speeds"].append(row.speed)
            data["battery"].append(row.battery)

        return Response(data)
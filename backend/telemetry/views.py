from rest_framework import generics
from .models import Telemetry
from .serializers import TelemetrySerializer

class TelemetryCreateView(generics.CreateAPIView):
    queryset = Telemetry.objects.all()
    serializer_class = TelemetrySerializer

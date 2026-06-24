from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlightViewSet, FlightTelemetryView, FlightAnalyticsView

app_name = 'flights'

router = DefaultRouter()
router.register(r'', FlightViewSet)

urlpatterns = [
    path('<int:pk>/telemetry/', FlightTelemetryView.as_view(), name='flight-telemetry'),
    path('<int:pk>/analytics/', FlightAnalyticsView.as_view(), name='flight-analytics'),
    path('', include(router.urls)),
]

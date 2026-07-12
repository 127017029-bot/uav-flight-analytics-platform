from django.urls import path
from .views import (
    TelemetryIngestView, TelemetryBatchIngestView,
    TelemetryListView, TelemetryLatestView,
    TelemetryStatsView, TelemetryChartDataView,
    DroneTelemetryChartDataView,
)

app_name = 'telemetry'

urlpatterns = [
    path('ingest/', TelemetryIngestView.as_view(), name='telemetry-ingest'),
    path('batch/', TelemetryBatchIngestView.as_view(), name='telemetry-batch'),
    path('list/', TelemetryListView.as_view(), name='telemetry-list'),
    path('latest/<int:drone_id>/', TelemetryLatestView.as_view(), name='telemetry-latest'),
    path('<int:drone_id>/latest/', TelemetryLatestView.as_view(), name='telemetry-latest-frontend'),
    path('stats/', TelemetryStatsView.as_view(), name='telemetry-stats'),
    path('<int:drone_id>/stats/', TelemetryStatsView.as_view(), name='telemetry-stats-frontend'),
    path('chart-data/<int:flight_id>/', TelemetryChartDataView.as_view(), name='telemetry-chart-data'),
    path('<int:drone_id>/chart/', DroneTelemetryChartDataView.as_view(), name='telemetry-chart-frontend'),
]

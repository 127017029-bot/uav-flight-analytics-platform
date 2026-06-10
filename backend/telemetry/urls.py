from django.urls import path
from .views import (
    TelemetryCreateView,
    TelemetryListView,
    TelemetryStatsView,
    TelemetryChartDataView
)

urlpatterns = [
    path('ingest/', TelemetryCreateView.as_view()),
    path('list/', TelemetryListView.as_view()),
    path('stats/', TelemetryStatsView.as_view()),
    path('chart-data/', TelemetryChartDataView.as_view()),
]
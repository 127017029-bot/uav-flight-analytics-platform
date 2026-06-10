from django.urls import path
from .views import TelemetryCreateView

urlpatterns = [
    path('ingest/', TelemetryCreateView.as_view()),
]
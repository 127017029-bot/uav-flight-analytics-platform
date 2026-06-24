"""Telemetry app configuration."""
from django.apps import AppConfig


class TelemetryConfig(AppConfig):
    """Configuration for the telemetry application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.telemetry'
    verbose_name = 'Telemetry Data'

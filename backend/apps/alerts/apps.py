"""Alerts app configuration."""
from django.apps import AppConfig


class AlertsConfig(AppConfig):
    """Configuration for the alerts application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.alerts'
    verbose_name = 'Alerts & Notifications'

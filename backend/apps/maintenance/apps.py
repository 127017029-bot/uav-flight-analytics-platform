"""Maintenance app configuration."""
from django.apps import AppConfig


class MaintenanceConfig(AppConfig):
    """Configuration for the maintenance application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.maintenance'
    verbose_name = 'Maintenance Records'

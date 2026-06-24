"""Drones app configuration."""
from django.apps import AppConfig


class DronesConfig(AppConfig):
    """Configuration for the drones application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.drones'
    verbose_name = 'Drones & Components'

"""Missions app configuration."""
from django.apps import AppConfig


class MissionsConfig(AppConfig):
    """Configuration for the missions application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.missions'
    verbose_name = 'Missions & Waypoints'

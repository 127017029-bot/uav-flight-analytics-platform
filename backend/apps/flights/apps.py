"""Flights app configuration."""
from django.apps import AppConfig


class FlightsConfig(AppConfig):
    """Configuration for the flights application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.flights'
    verbose_name = 'Flight Records'

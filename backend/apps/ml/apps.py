"""ML app configuration."""
from django.apps import AppConfig


class MlConfig(AppConfig):
    """Configuration for the machine learning application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ml'
    verbose_name = 'Machine Learning'

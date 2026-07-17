"""ML app configuration."""
from django.apps import AppConfig


class MlConfig(AppConfig):
    """Configuration for the machine learning application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ml'
    verbose_name = 'Machine Learning'

    def ready(self):
        # Model loading and database registration are handled lazily on demand
        # in apps.ml.registry to prevent Python import lock deadlocks on server startup.
        pass

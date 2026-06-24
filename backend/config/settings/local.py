"""
Local development settings using SQLite.
No PostgreSQL, Redis, or Celery required.
Just run: python manage.py runserver --settings=config.settings.local
"""

from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True

# ---- SQLite: zero-install, works immediately ----
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---- Disable Redis/Channels for local run ----
# Use in-memory channel layer (no Redis needed)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}

# ---- Disable Celery for local run ----
CELERY_TASK_ALWAYS_EAGER = True   # Run tasks synchronously
CELERY_TASK_EAGER_PROPAGATES = True

# ---- Email to console ----
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---- Show browsable API in browser ----
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
)

# ---- Remove custom exception handler (needs core app) ----
REST_FRAMEWORK.pop("EXCEPTION_HANDLER", None)  # noqa: F405

# ---- Silence missing static dir warning ----
STATICFILES_DIRS = []

# ---- Verbose logging ----
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}

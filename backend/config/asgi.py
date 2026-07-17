"""
ASGI config for the UAV Digital Twin Platform.

Exposes the ASGI callable as a module-level variable named ``application``.
Configures Django Channels ProtocolTypeRouter to handle both HTTP and
WebSocket connections for real-time telemetry streaming.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# Initialize Django ASGI application early to ensure apps are loaded
# before importing any channel routing.
django_asgi_app = get_asgi_application()

# Temporary isolation test: bypass Channels / ProtocolTypeRouter
# to isolate if the hang is caused by WebSocket or Channels initialization.
application = django_asgi_app

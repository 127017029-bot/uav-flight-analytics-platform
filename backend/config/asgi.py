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

# Import websocket routes after Django is initialised to avoid
# AppRegistryNotReady errors.
from apps.telemetry import routing as telemetry_routing  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                telemetry_routing.websocket_urlpatterns,
            )
        ),
    }
)

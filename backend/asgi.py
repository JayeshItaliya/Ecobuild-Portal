"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter

from cms.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Import get_asgi_application after setting DJANGO_SETTINGS_MODULE
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)

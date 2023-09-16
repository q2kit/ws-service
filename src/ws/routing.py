# chat/routing.py
from django.urls import path

from src.ws import consumers

websocket_urlpatterns = [
    path("ws/<str:project_id>/<str:token>", consumers.NotificationConsumer.as_asgi()),
]

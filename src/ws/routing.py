# chat/routing.py
from django.urls import path

from src.ws import consumers


websocket_urlpatterns = [
    path("ws/<str:project>/<str:token>", consumers.WSConsumer.as_asgi()),
]

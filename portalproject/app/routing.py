from django.urls import path

from . import consumers

websocket_urlpatterns = [
      path('ws/chat-server/', consumers.ChatConsumer.as_asgi()),

]
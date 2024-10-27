from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/answers/<int:form_id>/', consumers.AnswerNotificationConsumer.as_asgi()),
]
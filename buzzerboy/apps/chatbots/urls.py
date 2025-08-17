from django.urls import path
from buzzerboy.apps.chatbots.views import (
    HandleSlackEventView,
    HandleTeamsView,
)

app_name = 'chatbots'

urlpatterns = [
    path('slack/', HandleSlackEventView.as_view(), name='slack_bot'),
    path('teams/', HandleTeamsView.as_view(), name='teams_bot'),
]

# celery
from celery import shared_task

# django
from django.conf import settings

# slack
from slack_sdk import WebClient

# Slack API credentials
slack_client = WebClient(token=settings.SLACK_API_TOKEN)

@shared_task
def send_slack_message(channel, text):
    slack_client.chat_postMessage(channel=channel, text=text)

import json
import requests

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# botbuilder
from botbuilder.core import (
    TurnContext
)

# chatbots
from .tasks import send_slack_message
from .utils import (
    slack_amazon_titan_handler,
    slack_claude_handler,
)


BOT_PREAMBLE = """
    You are a friendly chatbot assistant. You will only help with work related questions.
    You will not answer any personal questions.
    You will not answer any questions that are not work related.
    You will not answer any questions that are not related to the company.
    You can help with mathematical calculations, programming questions, and general work-related queries.
    You can summarize documents, answer questions about company policies, and provide information about projects.
"""

class HandleSlackEventView(View):

    def post(self, request, *args, **kwargs):
        # Handle incoming Slack event
        event_data = json.loads(request.body)
        event_type = event_data['type']

        if event_type == 'url_verification':
            challenge = event_data['challenge']
            return HttpResponse(challenge)
        else:
            event = event_data['event']
            if event.get('type') == 'app_mention':
                channel = event.get('channel')
                
                # Claude
                # response_text = slack_claude_handler(event, BOT_PREAMBLE)

                # Amazon Titan
                response_text = slack_amazon_titan_handler(event, BOT_PREAMBLE)

                # We will use background task to send the message
                # so we can send the response without blocking
                # and Slack will not send duplicate messages
                send_slack_message.delay(channel, response_text)
        return HttpResponse('ok')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class HandleTeamsView(View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        # Handle Microsoft Teams event here
        # For example, you can extract the message and respond accordingly
        # This is a placeholder response
        print(data)
        conversation = data.get('conversation')
        payload = {
            "type": "message",
            "text": "Hello from the Teams bot!",
            "channelId": data.get('channelId'),
            "conversation": data.get('conversation'),
            "from": data.get('recipient'),
            "recipient": data.get('from'),
            "replyToId": data.get('id'),
            "recipient": data.get('from'),
        }
        service_url = data.get('serviceUrl')
        # service_url = f"{service_url}/directline/conversations/3754d620-79df-11f0-a438-1fb8208a6585/activities"
        response = requests.post(
            service_url,
            headers={
                'Authorization': f"Bearer {settings.SLACK_API_TOKEN}",
                'Content-Type': 'application/json'
            },
            json=payload
        )
        print(response.json())
        return HttpResponse(json.dumps(payload), status=200)
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

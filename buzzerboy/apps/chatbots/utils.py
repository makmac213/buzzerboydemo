import boto3
import docx
import json
import os
import pdfplumber
import requests
from django.conf import settings

# Amazon Bedrock API credentials
bedrock = boto3.client('bedrock-runtime', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=settings.AWS_SECRET_KEY,
                                 region_name=settings.AWS_REGION)


def extract_text_from_pdf(file_url):
    # Download the PDF file from Slack
    response = requests.get(file_url, headers={'Authorization': f'Bearer {settings.SLACK_API_TOKEN}'})
    print(response.status_code)
    print(file_url)
    file_path = '/tmp/temp.pdf'
    with open(file_path, 'wb') as f:
        f.write(response.content)

    file_size = os.path.getsize(file_path)
    print(file_size)

    # Extract text from the PDF file
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ''
            for page_number, page in enumerate(pdf.pages, start=1):
                text += page.extract_text()
            return text
    except Exception as e:
        print(e)
    return ""


def extract_text_from_docx(file_url):
    # Download the PDF file from Slack
    response = requests.get(file_url, headers={'Authorization': f'Bearer {SLACK_BOT_TOKEN}'})
    file_path = 'temp.docx'
    with open(file_path, 'wb') as f:
        f.write(response.content)

    doc = docx.Document('temp.docx')
    text = ""
    for para in doc.paragraphs:
        text += para.text
    return text

def slack_claude_handler(event, preamble=""):
    """Handle messages with claude"""
    BEDROCK_MODEL_ID = 'anthropic.claude-v2'
    message = event.get('text', '').split(' ')
    message = ' '.join(message)
    history = [
        f"Human: {preamble} Assistant: OK",
    ]
    file_url = event.get('files', [{}])[0].get('url_private')
    if file_url:
        # If there's an attachment, add it to the history
        history.append(f'Attachment: {file_url} Human: {message} Assistant:')
    else:
        history.append(f'Human: {message} Assistant:')
    body = json.dumps({
        "prompt": "".join(history),
        "max_tokens_to_sample": 2000,
        "temperature": 0.7,
        "top_p": 0.9
    })
    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        contentType='application/json',
        accept='application/json',
        body=body
    )
    response_body = json.loads(response['body'].read())
    response_text = ""
    response_type = response_body.get('type')
    if response_type == 'completion':
        response_text = response_body.get('completion')
    return response_text


def slack_amazon_titan_handler(event, preamble=""):
    """Handle message with titan"""
    BEDROCK_MODEL_ID = 'amazon.titan-text-express-v1'
    message = event.get('text', '').split(' ')
    message = ' '.join(message)

    text_generation_config = {
        "maxTokenCount": 2000,
        "temperature": 0.7,
        "topP": 0.9
    }

    # get file if any
    body = {
        "textGenerationConfig": text_generation_config,
    }
    file_url = event.get('files', [{}])[0].get('url_private')
    if file_url:
        file_type = event.get('files', [{}])[0].get('filetype')
        file_texts = ""
        if file_type == 'pdf':
            file_texts = extract_text_from_pdf(file_url)
        elif file_type == 'docx':
            file_texts = extract_text_from_docx(file_url)
        body['inputText'] = f"Given the content of the file '''{file_texts}'''. {message}"
    else:
        # no file
        body['inputText'] = f"PREAMBLE: {preamble}. {message}"
    response = bedrock.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        contentType='application/json',
        accept='application/json',
        body=json.dumps(body)
    )

    response_body = json.loads(response['body'].read())
    response_text = ""
    results = response_body.get('results')
    if len(results):
        result = results[0]
        response_text = result.get('outputText')
    return response_text
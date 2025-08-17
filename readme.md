## Lab 1

- Selected template is Kadso.
- Pages
  - Login page = /login/
  - Sign up page = /signup/
  - Dashboard, requires login = /dashboard/ 
  - My companies, requires login = /companies/
  - My profile = /my-profile/<company id>/
- Login via email. In the sign in page user will only need to enter his/her/their email and a login link will be sent via email (console for the demo)
- User profile model (Many-to-one User).
  - User needs to login first then click on the Companies on the sidebar. User clicks and adds new company and user will automatically linked to the new company created.
  - On the upper right corner click on the user's profile picture to view different company profiles.
  - User can switch default profile on the user's company profile page by clicking on the "Switch to this profile"
- Multilingualism
  - Current available languages are English (en) and Spanish (es).
  - On public pages (login, signup) there are flags there to switch the language.
  - Upon user's login, language will switch according to the current active profile's default language
- Initial Data Seeding
  - you can do this via ```python manage.py loaddata initial_data```
- requirements.txt has been updated. ```pip3 freeze > requirements.txt```
- It is ideal to setup with virtualenv and mkvirtualenv or best with Docker


## Lab 2

#### Install ngrok
  - Download and install ngrok from ngrok.com.
  - Run ngrok using the port of your Django development server ```ngrok http 8080```
  - Remember to add to allowed hosts the forwarding url to ALLOWED_HOSTS on settings.py

#### Setting up Slack
  - Go to https://slack.com/ and sign in or create a new account.
  - Create a new workspace
  - Go to https://api.slack.com/apps/ to create a new app.
  - Select "Event Subscriptions" on the sidebar.
  - Enable events then enter on the Request URL the forwarding url from ngrok. E.g. https://b1c45d83595a.ngrok-free.app/slack/
  - Then expand "Subscribe to bot events" and add the events app_mention and message.channels
  - Next go to OAuth & Permissions
  - Copy the OAuth token which will be the value for SLACK_API_TOKEN in settings.py
  - Under "Scopes" add the following scopes:
    - app_mentions:read
    - channels:history
    - chat:write
    - files:read
  - Click on "Install to <name of your slack app>" button
  - In your Slack channel, mention the name of your bot @Botname for example and add them to the channel.
  - You can now interact with your bot by mentioning it and give your prompt.

#### AWS
  - Sign in to console
  - Search for IAM and create a user
  - Under security credentials create an access key.
  - Take note of the access key id, access key secret and region. We will need this for our settings and when using boto3.

#### Redis and Celery
  - We added Redis and Celery to the project to handle asyncronous background tasks. We also need this so we could immediately send a 200 response to Slack to avoid duplicate events sent by them.

### Bedrock Models
  - At chatbots/utils.py for handling with models ```anthropic.claude-v2``` and ```amazon.titan-text-express-v1```

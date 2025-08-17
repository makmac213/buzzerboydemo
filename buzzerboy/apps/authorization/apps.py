from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'buzzerboy.apps.authorization'

    def ready(self):
        import buzzerboy.apps.authorization.signals

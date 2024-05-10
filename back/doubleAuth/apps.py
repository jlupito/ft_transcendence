from django.apps import AppConfig


class DoubleauthConfig(AppConfig):
    #default_auto_field = 'django.db.models.BigAutoField'
    name = 'doubleAuth'
    
    def ready(self):
        import doubleAuth.signals
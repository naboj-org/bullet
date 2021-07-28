from django.apps import AppConfig
from django.db import ProgrammingError


class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'web'

    def ready(self):
        from .dynamic_translations import init as trans_init
        try:
            trans_init()
        except ProgrammingError:
            # Table has not been created, some other manage.py command is being run
            pass

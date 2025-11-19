# app_financeiro/apps.py

from django.apps import AppConfig

class AppFinanceiroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_financeiro'

    def ready(self):
        # Esta linha é essencial para "ligar" os gatilhos automáticos
        import app_financeiro.signals
# app_contratos/apps.py

from django.apps import AppConfig

class AppContratosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_contratos'

    # --- ADICIONE ESTA FUNÇÃO ---
    def ready(self):
        import app_contratos.signals # Importa e ativa os sinais
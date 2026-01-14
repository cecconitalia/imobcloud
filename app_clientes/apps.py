from django.apps import AppConfig

class AppClientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_clientes'

    def ready(self):
        # Importa os sinais para que sejam registrados quando o app iniciar
        import app_clientes.signals
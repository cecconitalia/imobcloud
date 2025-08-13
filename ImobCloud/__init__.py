# ImobCloud/__init__.py

# Importa a app para garantir que ela é carregada quando o Django inicia
from .celery import app as celery_app

__all__ = ('celery_app',)
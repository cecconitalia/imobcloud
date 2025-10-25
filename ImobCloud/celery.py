# ImobCloud/celery.py

import os
from celery import Celery

# A CORREÇÃO ESTÁ AQUI: Apontamos para 'ImobCloud.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ImobCloud.settings')

# O nome do projeto é usado aqui
app = Celery('ImobCloud')

# Usamos o namespace 'CELERY' para que todas as configurações do Celery no settings.py
# comecem com CELERY_ (ex: CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Carrega módulos de tarefas de todas as apps Django registadas.
app.autodiscover_tasks()
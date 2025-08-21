# C:\wamp64\www\ImobCloud\app_boletos\urls.py

from django.urls import path
from .views import GerarBoletoView

urlpatterns = [
    # Rota para a view de geração de boleto
    path('gerar/', GerarBoletoView.as_view(), name='gerar-boleto'),
]
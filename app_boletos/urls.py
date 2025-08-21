# C:\wamp64\www\ImobCloud\app_boletos\urls.py

from django.urls import path
from .views import GerarBoletoView, ConfiguracaoBancoListView

urlpatterns = [
    # Rota para listar as configurações de banco
    path('configuracoes-banco/', ConfiguracaoBancoListView.as_view(), name='configuracoes-banco'),

    # Rota para a view de geração de boleto
    path('gerar/', GerarBoletoView.as_view(), name='gerar-boleto'),
]
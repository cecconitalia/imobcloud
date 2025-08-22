# C:\wamp64\www\ImobCloud\app_boletos\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GerarBoletoView, ConfiguracaoBancoListView, ConfiguracaoBancoViewSet

# NOVO: Crie um router para o ViewSet
router = DefaultRouter()
router.register(r'configuracoes-banco', ConfiguracaoBancoViewSet, basename='configuracoes-banco')


urlpatterns = [
    # Rotas geradas pelo router
    path('', include(router.urls)),

    # Rota para a view de geração de boleto
    path('gerar/', GerarBoletoView.as_view(), name='gerar-boleto'),
]
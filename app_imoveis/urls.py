# C:\wamp64\www\ImobCloud\app_imoveis\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# ATUALIZADO: Importar a nova View
from .views import ImovelViewSet, ImagemImovelViewSet, ContatoImovelViewSet, GerarAutorizacaoPDFView, AutorizacaoStatusView

router = DefaultRouter()
router.register(r'imoveis', ImovelViewSet)
router.register(r'imagens', ImagemImovelViewSet)
router.register(r'contatos', ContatoImovelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('imoveis/<int:imovel_id>/gerar-autorizacao-pdf/', GerarAutorizacaoPDFView.as_view(), name='gerar-autorizacao-pdf'),
    
    # ROTA QUE ESTAVA EM FALTA ADICIONADA AQUI
    path('relatorio-autorizacoes/', AutorizacaoStatusView.as_view(), name='relatorio-autorizacoes'),
]
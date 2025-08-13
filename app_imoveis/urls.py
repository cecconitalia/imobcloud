from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ImovelViewSet,
    ImagemImovelViewSet,
    ContatoImovelViewSet,
    GerarAutorizacaoPDFView,
    AutorizacaoStatusView
)

# O DefaultRouter cria automaticamente as URLs para o seu ViewSet.
# Ex: /imoveis/, /imoveis/{id}/, etc.
router = DefaultRouter()
router.register(r'imoveis', ImovelViewSet, basename='imovel')
router.register(r'imagens', ImagemImovelViewSet, basename='imagemimovel')
router.register(r'contatos', ContatoImovelViewSet, basename='contatoimovel')

# O urlpatterns começa com as rotas geradas pelo router.
urlpatterns = [
    # Inclui as rotas geradas automaticamente (ex: /api/v1/imoveis/, /api/v1/imoveis/1/)
    path('', include(router.urls)),
    
    # Adicionamos as rotas para as suas views específicas (APIViews)
    path('imoveis/autorizacao-pdf/<int:imovel_id>/', GerarAutorizacaoPDFView.as_view(), name='gerar-autorizacao-pdf'),
    path('imoveis/autorizacoes/status/', AutorizacaoStatusView.as_view(), name='autorizacao-status'),
]
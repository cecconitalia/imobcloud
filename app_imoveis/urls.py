from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ImovelViewSet, 
    ImagemImovelViewSet, 
    ContatoImovelViewSet,
    ImovelPublicListView,
    ImovelPublicDetailView,
    GerarAutorizacaoPDFView,
    AutorizacaoStatusView
)

# O DefaultRouter cria automaticamente as URLs para todas as ações em um ViewSet
router = DefaultRouter()

# Registra os endpoints principais para o painel administrativo
router.register(r'imoveis', ImovelViewSet, basename='imovel')

# CORREÇÃO: Registra a ViewSet de imagens no roteador.
# Isso cria a rota '/api/v1/imoveis/imagens/' e habilita o método POST,
# resolvendo o erro "405 Method Not Allowed".
router.register(r'imagens', ImagemImovelViewSet, basename='imagemimovel')

router.register(r'contatos', ContatoImovelViewSet, basename='contatoimovel')

# URLs da aplicação
urlpatterns = [
    # Inclui todas as URLs geradas pelo roteador para o painel administrativo
    # Ex: /api/v1/imoveis/imoveis/, /api/v1/imoveis/imagens/, etc.
    path('', include(router.urls)),

    # Mantém as URLs públicas e outras views customizadas que não usam ViewSet
    path('public/imoveis/', ImovelPublicListView.as_view(), name='imovel-public-list'),
    path('public/imoveis/<int:pk>/', ImovelPublicDetailView.as_view(), name='imovel-public-detail'),
    path('imoveis/<int:imovel_id>/gerar-autorizacao-pdf/', GerarAutorizacaoPDFView.as_view(), name='gerar-autorizacao-pdf'),
    path('autorizacao-status/', AutorizacaoStatusView.as_view(), name='autorizacao-status'),
]
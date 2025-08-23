# app_imoveis/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ImovelViewSet,
    ImagemImovelViewSet,
    ContatoImovelViewSet,
    ImovelPublicListView,
    ImovelPublicDetailView,
    GerarAutorizacaoPDFView,
    AutorizacaoStatusView,
    ImovelIAView,
)

router = DefaultRouter()

# Registros no router
router.register(r'imoveis', ImovelViewSet, basename='imovel')
# ESTA É A ROTA NOVA E CORRETA PARA AS IMAGENS
router.register(r'imagens-imovel', ImagemImovelViewSet, basename='imagemimovel')
router.register(r'contatos', ContatoImovelViewSet, basename='contatoimovel')

urlpatterns = [
    # Inclui as URLs do router
    path('', include(router.urls)),

    # Mantém as URLs customizadas
    path('public/imoveis/', ImovelPublicListView.as_view(), name='imovel-public-list'),
    path('public/imoveis/<int:pk>/', ImovelPublicDetailView.as_view(), name='imovel-public-detail'),
    path('imoveis/<int:imovel_id>/gerar-autorizacao-pdf/', GerarAutorizacaoPDFView.as_view(), name='gerar-autorizacao-pdf'),
    path('autorizacao-status/', AutorizacaoStatusView.as_view(), name='autorizacao-status'),

    # ROTA NOVA PARA BUSCA COM IA
    # CORRIGIDO: A rota agora está sob o prefixo 'public/'
    path('public/imoveis/busca-ia/', ImovelIAView.as_view(), name='imovel-busca-ia')
]
# app_imoveis/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ImovelViewSet,
    ImagemImovelViewSet,
    ContatoImovelViewSet,
    GerarAutorizacaoPDFView,
    AutorizacaoStatusView,
    ImovelPublicListView,
    ImovelPublicDetailView,
    ImovelIAView,
    ImobiliariaPublicDetailView,
)

router = DefaultRouter()
router.register(r'imoveis', ImovelViewSet, basename='imoveis')
router.register(r'imagens', ImagemImovelViewSet, basename='imagens')
router.register(r'contatos', ContatoImovelViewSet, basename='contatos')

urlpatterns = [
    # Rotas da API Interna
    path('', include(router.urls)),
    path('imoveis/<int:imovel_id>/gerar-pdf-autorizacao/', GerarAutorizacaoPDFView.as_view(), name='gerar-pdf-autorizacao'),
    path('autorizacao-status/', AutorizacaoStatusView.as_view(), name='autorizacao-status'),

    # Rotas da API Pública (Sem Autenticação)
    # A ROTA MAIS ESPECÍFICA (busca-ia) DEVE VIR ANTES DA ROTA GENÉRICA (<int:pk>)
    path('public/imoveis/busca-ia/', ImovelIAView.as_view(), name='imovel-busca-ia'),
    path('public/imoveis/', ImovelPublicListView.as_view(), name='imovel-public-list'),
    path('public/imoveis/<int:pk>/', ImovelPublicDetailView.as_view(), name='imovel-public-detail'),
    
    # Rota para obter detalhes da imobiliária pelo subdomínio (ADICIONADO)
    path('public/imobiliaria/<str:subdominio>/', ImobiliariaPublicDetailView.as_view(), name='imobiliaria-public-detail'),
]
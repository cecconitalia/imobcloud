# C:\wamp64\www\ImobCloud\app_imoveis\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ImovelViewSet, 
    ImagemImovelViewSet, 
    ContatoImovelViewSet, 
    GerarAutorizacaoPDFView, 
    ImovelPublicListView,
    ImovelPublicDetailView,
    ImovelIAView,
    AutorizacaoReportView,
    AutorizacaoReportPDFView,
)

# Cria um router para ViewSets
router = DefaultRouter()
router.register(r'imoveis', ImovelViewSet)
router.register(r'imoveis/imagens', ImagemImovelViewSet)
router.register(r'contatos', ContatoImovelViewSet)

urlpatterns = [
    # 1. Rota Explícita para a Geração de PDF (Contrato individual de um imóvel)
    path(
        'imoveis/<int:imovel_id>/gerar-autorizacao-pdf/', 
        GerarAutorizacaoPDFView.as_view(), 
        name='gerar-autorizacao-pdf'
    ),
    
    # 2. Rota do Relatório de Autorizações (JSON - Dados para a tabela)
    path(
        'imoveis/relatorio/autorizacoes/', 
        AutorizacaoReportView.as_view(), 
        name='relatorio-autorizacoes'
    ),
    
    # 3. Rota do Relatório Geral de Autorizações (PDF - Botão Imprimir)
    # CORREÇÃO: Adicionada a rota exata que o frontend está chamando
    path(
        'imoveis/relatorio-geral-autorizacoes/', 
        AutorizacaoReportPDFView.as_view(), 
        name='relatorio-geral-autorizacoes-pdf'
    ),
    
    # 4. Rotas automáticas do ViewSet (Cria, Lista, Detalhe, Update, etc.)
    path('', include(router.urls)),
    
    # --- Rotas Públicas ---
    path('public/imoveis/', ImovelPublicListView.as_view(), name='imovel-public-list'),
    path('public/imoveis/<int:pk>/', ImovelPublicDetailView.as_view(), name='imovel-public-detail'),
    path('public/imoveis/busca-ia/', ImovelIAView.as_view(), name='imovel-ia-search'),
]
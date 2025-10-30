# C:\wamp64\www\ImobCloud\app_imoveis\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ImovelViewSet, 
    ImagemImovelViewSet, 
    ContatoImovelViewSet, 
    GerarAutorizacaoPDFView, # Importado para mapeamento
    ImovelPublicListView,
    ImovelPublicDetailView,
    ImovelIAView,
    AutorizacaoReportView, # <-- IMPORTAÇÃO ADICIONADA
    AutorizacaoReportPDFView, # <-- IMPORTAÇÃO ADICIONADA
)

# Cria um router para ViewSets
router = DefaultRouter()
router.register(r'imoveis', ImovelViewSet)
router.register(r'imoveis/imagens', ImagemImovelViewSet)
router.register(r'imoveis/contatos', ContatoImovelViewSet)

# Padrões de URL da API Interna (Prefixados com /api/v1/ no urls.py principal)
urlpatterns = [
    # 1. Rota Explícita para a Geração de PDF (Contrato individual)
    path(
        'imoveis/<int:imovel_id>/gerar-autorizacao-pdf/', 
        GerarAutorizacaoPDFView.as_view(), 
        name='gerar-autorizacao-pdf'
    ),
    
    # 2. Rota do Relatório de Autorizações (JSON)
    path(
        'imoveis/relatorio/autorizacoes/', 
        AutorizacaoReportView.as_view(), 
        name='relatorio-autorizacoes'
    ),
    
    # 3. Rota do Relatório de Autorizações (PDF)
    path(
        'imoveis/relatorio/autorizacoes/pdf/', 
        AutorizacaoReportPDFView.as_view(), 
        name='relatorio-autorizacoes-pdf'
    ),
    
    # 4. Rotas automáticas do ViewSet (Cria, Lista, Detalhe, Update, IA Action)
    path('', include(router.urls)),
    
    # --- Rotas Públicas (Se necessário, você as mapeia separadamente) ---
    path('public/imoveis/', ImovelPublicListView.as_view(), name='imovel-public-list'),
    path('public/imoveis/<int:pk>/', ImovelPublicDetailView.as_view(), name='imovel-public-detail'),
    path('public/imoveis/busca-ia/', ImovelIAView.as_view(), name='imovel-ia-search'),
]
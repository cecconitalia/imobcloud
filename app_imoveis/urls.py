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
    GetAutorizacaoHtmlView,       # View Nova
    SalvarAutorizacaoHtmlView,    # View Nova
    VisualizarAutorizacaoPdfView, # View Nova
)

# Cria um router para ViewSets
router = DefaultRouter()
router.register(r'imoveis', ImovelViewSet)
router.register(r'imoveis/imagens', ImagemImovelViewSet)
router.register(r'contatos', ContatoImovelViewSet)

urlpatterns = [
    # 1. Rota Antiga/Compatibilidade (Geração Direta sem Editor)
    path(
        'imoveis/<int:imovel_id>/gerar-autorizacao-pdf/', 
        GerarAutorizacaoPDFView.as_view(), 
        name='gerar-autorizacao-pdf'
    ),
    
    # --- NOVAS ROTAS DO EDITOR DE AUTORIZAÇÃO ---
    path(
        'imoveis/<int:pk>/get-autorizacao-html/',
        GetAutorizacaoHtmlView.as_view(),
        name='get-autorizacao-html'
    ),
    path(
        'imoveis/<int:pk>/salvar-autorizacao-html/',
        SalvarAutorizacaoHtmlView.as_view(),
        name='salvar-autorizacao-html'
    ),
    path(
        'imoveis/<int:pk>/visualizar-autorizacao-pdf/',
        VisualizarAutorizacaoPdfView.as_view(),
        name='visualizar-autorizacao-pdf'
    ),
    # --------------------------------------------

    # 2. Rota do Relatório de Autorizações (JSON - Dados para a tabela)
    path(
        'imoveis/relatorio/autorizacoes/', 
        AutorizacaoReportView.as_view(), 
        name='relatorio-autorizacoes'
    ),
    
    # 3. Rota do Relatório Geral de Autorizações (PDF - Botão Imprimir)
    path(
        'imoveis/relatorio-geral-autorizacoes/', 
        AutorizacaoReportPDFView.as_view(), 
        name='relatorio-geral-autorizacoes-pdf'
    ),
    
    # 4. Rotas automáticas do ViewSet (Cria, Lista, Detalhe, Update, etc.)
    # ATENÇÃO: O include do router deve vir DEPOIS das rotas manuais específicas de 'imoveis/'
    path('', include(router.urls)),
    
    # --- Rotas Públicas ---
    path('public/imoveis/', ImovelPublicListView.as_view(), name='imovel-public-list'),
    path('public/imoveis/<int:pk>/', ImovelPublicDetailView.as_view(), name='imovel-public-detail'),
    path('public/imoveis/busca-ia/', ImovelIAView.as_view(), name='imovel-ia-search'),
]
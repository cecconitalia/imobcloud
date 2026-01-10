# app_financeiro/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransacaoViewSet, CategoriaViewSet, ContaViewSet, FormaPagamentoViewSet, DREViewAPI

# Configuração do Router
router = DefaultRouter()
router.register(r'transacoes', TransacaoViewSet, basename='transacao')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'contas', ContaViewSet, basename='conta')
router.register(r'formas-pagamento', FormaPagamentoViewSet, basename='formapagamento')

urlpatterns = [
    # --- ROTAS EXPLÍCITAS E PRIORITÁRIAS (Fix 404) ---
    # Estas rotas DEVEM vir antes do router.urls
    
    # Rota para Contas a Receber
    path('transacoes/a-receber/', TransacaoViewSet.as_view({'get': 'a_receber'}), name='transacoes-a-receber'),
    
    # Rota para Contas a Pagar
    path('transacoes/a-pagar/', TransacaoViewSet.as_view({'get': 'a_pagar'}), name='transacoes-a-pagar'),
    
    # Rota para Dashboard Stats (Geral)
    path('transacoes/dashboard-general-stats/', TransacaoViewSet.as_view({'get': 'dashboard_general_stats'}), name='transacoes-dashboard-general-stats'),
    
    # Rota para Stats Financeiros
    path('transacoes/stats/', TransacaoViewSet.as_view({'get': 'stats'}), name='transacoes-stats'),

    # --- ROTAS AUTOMÁTICAS DO ROUTER ---
    path('', include(router.urls)),
    
    # --- OUTRAS ROTAS MANUAIS ---
    path('dre/', DREViewAPI.as_view(), name='dre-api'),
]
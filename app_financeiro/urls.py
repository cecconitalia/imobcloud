from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransacaoViewSet, 
    CategoriaViewSet, 
    ContaViewSet, 
    FormaPagamentoViewSet, 
    DREViewAPI,
    FinanceiroStatsView # Importante: View criada para o dashboard principal
)

# Configuração do Router
router = DefaultRouter()
router.register(r'transacoes', TransacaoViewSet, basename='transacao')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'contas', ContaViewSet, basename='conta')
router.register(r'formas-pagamento', FormaPagamentoViewSet, basename='formapagamento')

urlpatterns = [
    # --- ROTA DE ESTATÍSTICAS GERAIS (Dashboard) ---
    # Esta rota deve ficar no topo para garantir que /financeiro/stats/ 
    # seja resolvida antes de entrar no router ou em outras sub-rotas.
    path('stats/', FinanceiroStatsView.as_view(), name='financeiro-stats'),

    # --- ROTAS EXPLÍCITAS E PRIORITÁRIAS (Transações) ---
    # Estas rotas garantem acesso direto às actions sem depender da regex do Router
    path('transacoes/a-receber/', TransacaoViewSet.as_view({'get': 'a_receber'}), name='transacoes-a-receber'),
    path('transacoes/a-pagar/', TransacaoViewSet.as_view({'get': 'a_pagar'}), name='transacoes-a-pagar'),
    path('transacoes/dashboard-general-stats/', TransacaoViewSet.as_view({'get': 'dashboard_general_stats'}), name='transacoes-dashboard-general-stats'),
    
    # Rota legada/específica do viewset (caso o frontend chame transacoes/stats/)
    path('transacoes/stats/', TransacaoViewSet.as_view({'get': 'stats'}), name='transacoes-stats-viewset'),

    # --- RELATÓRIOS ---
    path('dre/', DREViewAPI.as_view(), name='dre-api'),

    # --- ROTAS AUTOMÁTICAS DO ROUTER ---
    path('', include(router.urls)),
]
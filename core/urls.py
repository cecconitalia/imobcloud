from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardStatsView, 
    CorretorRegistrationViewSet, 
    IntegracaoRedesSociaisView,
    PublicRegisterView,
    MarcarNotificacaoLidaView,
    MinhasNotificacoesView,
    ConfiguracaoGlobalView,
    # Novos ViewSets
    ImobiliariaViewSet,
    ConfiguracaoGlobalViewSet
)

# Configuração do Router
router = DefaultRouter()

# Registra 'usuarios'. URL: /api/v1/core/usuarios/
router.register(r'usuarios', CorretorRegistrationViewSet, basename='usuario')

# Registra 'imobiliarias'. URL: /api/v1/core/imobiliarias/
# Isso habilita o endpoint: /api/v1/core/imobiliarias/me/
router.register(r'imobiliarias', ImobiliariaViewSet, basename='imobiliaria')

# Registra configuração global (somente leitura via viewset, ou use a view manual abaixo)
router.register(r'config-publica', ConfiguracaoGlobalViewSet, basename='config-publica')

urlpatterns = [
    # --- Rotas Específicas (Manuais) ---

    # Notificações
    path('usuarios/marcar-notificacao-lida/<int:pk>/', MarcarNotificacaoLidaView.as_view(), name='marcar-notificacao-lida'),
    path('minhas-notificacoes/', MinhasNotificacoesView.as_view(), name='minhas-notificacoes-manual'),
    
    # Estatísticas do Dashboard
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats_core'),
    
    # Integrações por Tenant (Facebook/Instagram)
    path('integracoes/redes-sociais/', IntegracaoRedesSociaisView.as_view(), name='integracoes-redes-sociais'),
    
    # Configuração Global (Edição via painel admin/superuser)
    path('configuracao-global/', ConfiguracaoGlobalView.as_view(), name='configuracao-global'),

    # Cadastro Público (SaaS)
    path('public-register/', PublicRegisterView.as_view(), name='public-register'),
    
    # --- Router (Fica por último) ---
    path('', include(router.urls)),
]
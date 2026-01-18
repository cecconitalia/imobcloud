# C:\wamp64\www\ImobCloud\core\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardStatsView, 
    CorretorRegistrationViewSet, 
    IntegracaoRedesSociaisView,
    PublicRegisterView,
    MarcarNotificacaoLidaView,
    MinhasNotificacoesView,
    ConfiguracaoGlobalView
)

# Configuração do Router
router = DefaultRouter()
# Registra 'usuarios'. A URL final será /api/v1/core/usuarios/
# O router gera automaticamente endpoints como:
# - GET /usuarios/me/ (Perfil do usuário logado)
# - GET /usuarios/minhas-notificacoes/ (Notificações do usuário)
router.register(r'usuarios', CorretorRegistrationViewSet, basename='usuario')

urlpatterns = [
    # --- Rotas Específicas (Manuais) ---

    # Notificações (Endpoints manuais caso não use via ViewSet)
    path('usuarios/marcar-notificacao-lida/<int:pk>/', MarcarNotificacaoLidaView.as_view(), name='marcar-notificacao-lida'),
    path('minhas-notificacoes/', MinhasNotificacoesView.as_view(), name='minhas-notificacoes-manual'),
    
    # Estatísticas do Dashboard (Rota auxiliar para chamadas diretas ao core)
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats_core'),
    
    # Integrações por Tenant (Facebook/Instagram)
    path('integracoes/redes-sociais/', IntegracaoRedesSociaisView.as_view(), name='integracoes-redes-sociais'),
    
    # Configuração Global (Substituição de variáveis de ambiente via painel)
    path('configuracao-global/', ConfiguracaoGlobalView.as_view(), name='configuracao-global'),

    # Cadastro Público (Rota de Registro via Core)
    # Nota: A rota principal usada pelo frontend está mapeada no urls.py raiz,
    # mas mantemos esta aqui como fallback acessível via /api/v1/core/public-register/
    path('public-register/', PublicRegisterView.as_view(), name='public-register'),
    
    # --- Router (Deve ficar por último para não engolir rotas manuais) ---
    path('', include(router.urls)),
]
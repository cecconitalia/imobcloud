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
# O router gera automaticamente: /usuarios/me/ e /usuarios/minhas-notificacoes/
router.register(r'usuarios', CorretorRegistrationViewSet, basename='usuario')

urlpatterns = [
    # Rotas manuais que NÃO estão no ViewSet
    path('usuarios/marcar-notificacao-lida/<int:pk>/', MarcarNotificacaoLidaView.as_view(), name='marcar-notificacao-lida'),
    
    # Rota auxiliar de estatísticas (caso o frontend chame via core)
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats_core'),
    
    # Integrações por Tenant
    path('integracoes/redes-sociais/', IntegracaoRedesSociaisView.as_view(), name='integracoes-redes-sociais'),
    
    # Configuração Global (Substituição .env)
    path('configuracao-global/', ConfiguracaoGlobalView.as_view(), name='configuracao-global'),

    # Cadastro Público
    path('public-register/', PublicRegisterView.as_view(), name='public-register'),
    
    # Inclui as rotas do Router por último para evitar conflitos
    path('', include(router.urls)),
]
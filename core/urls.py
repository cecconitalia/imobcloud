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
    ImobiliariaViewSet,
    ConfiguracaoGlobalViewSet,
    PerfilUsuarioViewSet,
    NotificacaoViewSet,
    PlanoViewSet
)

# ==============================================================================
# CONFIGURAÇÃO DO ROUTER (DRF)
# ==============================================================================
router = DefaultRouter()

# Gerenciamento da Imobiliária (Tenant)
# URL Base: /api/v1/core/imobiliarias/
# Action: /api/v1/core/imobiliarias/minha-imobiliaria/ (Configurações do Sistema)
router.register(r'imobiliarias', ImobiliariaViewSet, basename='imobiliaria')

# Gerenciamento de Usuários (Corretores/Admins) - Visão Administrativa
# URL Base: /api/v1/core/usuarios/
router.register(r'usuarios', CorretorRegistrationViewSet, basename='usuario')

# Perfil do Usuário Logado - Visão Pessoal
# URL Base: /api/v1/core/perfil/
router.register(r'perfil', PerfilUsuarioViewSet, basename='perfil')

# Configurações Públicas (Logo, Título do Sistema)
# URL Base: /api/v1/core/configuracoes-globais/
router.register(r'configuracoes-globais', ConfiguracaoGlobalViewSet, basename='config-global')

# Notificações
# URL Base: /api/v1/core/notificacoes/
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacao')

# Planos e Assinaturas
# URL Base: /api/v1/core/planos/
router.register(r'planos', PlanoViewSet, basename='plano')

# ==============================================================================
# URL PATTERNS
# ==============================================================================
urlpatterns = [
    # --- Funcionalidades Específicas (Views Manuais) ---

    # Notificações (Endpoints diretos)
    path('usuarios/marcar-notificacao-lida/<int:pk>/', MarcarNotificacaoLidaView.as_view(), name='marcar-notificacao-lida'),
    path('minhas-notificacoes/', MinhasNotificacoesView.as_view(), name='minhas-notificacoes-manual'),
    
    # Dashboard e Estatísticas
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats_core'),
    
    # Integrações (Facebook/Instagram/Gemini)
    path('integracoes/redes-sociais/', IntegracaoRedesSociaisView.as_view(), name='integracoes-redes-sociais'),
    
    # Configuração Global (Legado/Manutenção)
    path('configuracao-global/', ConfiguracaoGlobalView.as_view(), name='configuracao-global'),

    # Cadastro Público (SaaS - Self Service)
    path('public-register/', PublicRegisterView.as_view(), name='public-register'),
    
    # --- Router (Endpoints Automáticos) ---
    # O include do router deve ficar por último para não interceptar rotas manuais específicas
    path('', include(router.urls)),
]
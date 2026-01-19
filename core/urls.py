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
    PerfilUsuarioViewSet
)

# ==============================================================================
# CONFIGURAÇÃO DO ROUTER (DRF)
# ==============================================================================
router = DefaultRouter()

# Gerenciamento de Usuários (Corretores/Admins)
# URL Base: /api/v1/core/usuarios/
# Inclui actions como: /usuarios/me/, /usuarios/minhas-notificacoes/
router.register(r'usuarios', CorretorRegistrationViewSet, basename='usuario')

# Perfil do Usuário (Alternativa focada no próprio usuário e edição de perfil)
# URL Base: /api/v1/core/perfil/
router.register(r'perfil', PerfilUsuarioViewSet, basename='perfil')

# Gerenciamento da Imobiliária (Tenant)
# URL Base: /api/v1/core/imobiliarias/
# Endpoint Principal: /api/v1/core/imobiliarias/me/ (Edição da própria empresa)
router.register(r'imobiliarias', ImobiliariaViewSet, basename='imobiliaria')

# Configurações Públicas (Logo, Título do Sistema)
# URL Base: /api/v1/core/config-publica/
router.register(r'config-publica', ConfiguracaoGlobalViewSet, basename='config-publica')

# ==============================================================================
# URL PATTERNS
# ==============================================================================
urlpatterns = [
    # --- Funcionalidades Específicas (Views Manuais) ---

    # Notificações (Endpoints diretos para facilitar integração)
    path('usuarios/marcar-notificacao-lida/<int:pk>/', MarcarNotificacaoLidaView.as_view(), name='marcar-notificacao-lida'),
    path('minhas-notificacoes/', MinhasNotificacoesView.as_view(), name='minhas-notificacoes-manual'),
    
    # Dashboard e Estatísticas
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats_core'),
    
    # Integrações (Facebook/Instagram/Gemini)
    path('integracoes/redes-sociais/', IntegracaoRedesSociaisView.as_view(), name='integracoes-redes-sociais'),
    
    # Configuração Global (Legado/Manutenção - Edição via superuser)
    path('configuracao-global/', ConfiguracaoGlobalView.as_view(), name='configuracao-global'),

    # Cadastro Público (SaaS - Self Service)
    # Permite criar Imobiliária + Usuário Admin sem autenticação
    path('public-register/', PublicRegisterView.as_view(), name='public-register'),
    
    # --- Router (Endpoints Automáticos) ---
    # É importante ficar por último para não sobrescrever rotas específicas
    path('', include(router.urls)),
]
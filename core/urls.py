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
    PlanoViewSet,
    LogoutView
)
from app_imoveis.views import PublicImovelViewSet

# Router Principal
router = DefaultRouter()

# ... (Mantenha seus registros existentes de imobiliarias, usuarios, etc) ...
router.register(r'imobiliarias', ImobiliariaViewSet, basename='imobiliaria')
router.register(r'usuarios', CorretorRegistrationViewSet, basename='usuario')
router.register(r'perfil', PerfilUsuarioViewSet, basename='perfil')
router.register(r'configuracoes-globais', ConfiguracaoGlobalViewSet, basename='config-global')
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacao')
router.register(r'planos', PlanoViewSet, basename='plano')

# --- ROTA PÚBLICA (CRUCIAL) ---
# Registrando aqui, ela ficará disponível em /public/imoveis/
# pois o include(router.urls) está na raiz urlpatterns
router.register(r'public/imoveis', PublicImovelViewSet, basename='public-imoveis')

urlpatterns = [
    # Views Manuais
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('usuarios/marcar-notificacao-lida/<int:pk>/', MarcarNotificacaoLidaView.as_view(), name='marcar-notificacao-lida'),
    path('minhas-notificacoes/', MinhasNotificacoesView.as_view(), name='minhas-notificacoes-manual'),
    path('integracoes/redes-sociais/', IntegracaoRedesSociaisView.as_view(), name='integracoes-redes-sociais'),
    path('configuracao-global/', ConfiguracaoGlobalView.as_view(), name='configuracao-global'),
    path('public-register/', PublicRegisterView.as_view(), name='public-register'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    
    # Rota API (Opcional, se você quiser acessar via /api/public/imoveis também)
    path('api/', include(router.urls)),

    # Rota Raiz (Isso faz o public/imoveis funcionar direto na raiz)
    path('', include(router.urls)),
]
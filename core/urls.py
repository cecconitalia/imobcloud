# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# CORREÇÃO:
# 1. Importar 'CorretorRegistrationViewSet' (que tem a lógica) em vez de 'CorretorViewSet'.
# 2. Remover a importação de 'NotificacaoViewSet' (que não existe).
from .views import DashboardStatsView, CorretorRegistrationViewSet, IntegracaoRedesSociaisView

router = DefaultRouter()

# CORREÇÃO: Registrar o 'CorretorRegistrationViewSet' para que as rotas
# 'me', 'minhas_notificacoes', etc., funcionem.
router.register(r'corretores', CorretorRegistrationViewSet, basename='corretor')

# REMOVIDO: O ViewSet 'NotificacaoViewSet' não existe mais.
# router.register(r'notificacoes', NotificacaoViewSet, basename='notificacao')

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('integracoes/redes-sociais/', IntegracaoRedesSociaisView.as_view(), name='integracoes-redes-sociais'),
    path('', include(router.urls)),
]
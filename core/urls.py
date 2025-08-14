# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardStatsView, CorretorViewSet, NotificacaoViewSet, IntegracaoRedesSociaisView

router = DefaultRouter()
router.register(r'corretores', CorretorViewSet, basename='corretor')
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacao')

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('integracoes/redes-sociais/', IntegracaoRedesSociaisView.as_view(), name='integracoes-redes-sociais'),
    path('', include(router.urls)),
]
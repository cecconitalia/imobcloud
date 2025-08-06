# C:\wamp64\www\ImobCloud\core\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# ATUALIZADO: Importar o CorretorViewSet e a nova NotificacaoViewSet
from .views import DashboardStatsView, CorretorViewSet, NotificacaoViewSet

router = DefaultRouter()
router.register(r'corretores', CorretorViewSet, basename='corretor')
# NOVO: Registrar a ViewSet para as notificações
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacao')

urlpatterns = [
    # URL para as estatísticas do dashboard
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    
    # Inclui todas as URLs geradas pelo router (para corretores e notificações)
    path('', include(router.urls)),
]
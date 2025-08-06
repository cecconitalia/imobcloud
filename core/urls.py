# C:\wamp64\www\ImobCloud\core\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# ATUALIZADO: Importar o CorretorViewSet
from .views import DashboardStatsView, CorretorViewSet

router = DefaultRouter()
# NOVO: Registrar o ViewSet para os utilizadores
router.register(r'corretores', CorretorViewSet, basename='corretor')

urlpatterns = [
    # URL para as estatísticas do dashboard
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    
    # URL para o registo e listagem de corretores (agora via ViewSet)
    path('', include(router.urls)),
]
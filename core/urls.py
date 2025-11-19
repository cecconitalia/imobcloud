# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardStatsView, CorretorRegistrationViewSet, IntegracaoRedesSociaisView

router = DefaultRouter()

# CORREÇÃO: Alterado de 'corretores' para 'core/usuarios' para corresponder 
# à chamada do frontend: /api/v1/core/usuarios/
router.register(r'core/usuarios', CorretorRegistrationViewSet, basename='usuario')

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('integracoes/redes-sociais/', IntegracaoRedesSociaisView.as_view(), name='integracoes-redes-sociais'),
    path('', include(router.urls)),
]
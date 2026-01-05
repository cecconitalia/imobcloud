# C:\wamp64\www\ImobCloud\core\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardStatsView, 
    CorretorRegistrationViewSet, 
    IntegracaoRedesSociaisView,
    PublicRegisterView # Importação da Nova View
)

router = DefaultRouter()
router.register(r'core/usuarios', CorretorRegistrationViewSet, basename='usuario')

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('integracoes/redes-sociais/', IntegracaoRedesSociaisView.as_view(), name='integracoes-redes-sociais'),
    
    # Nova Rota Pública para Cadastro
    path('public/register/', PublicRegisterView.as_view(), name='public-register'),
    
    path('', include(router.urls)),
]
# C:\wamp64\www\ImobCloud\core\urls.py

from django.urls import path
from .views import DashboardStatsView, CorretorRegistrationView # NOVO: Importamos a nova view

urlpatterns = [
    # URL para as estatísticas do dashboard
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    
    # NOVO: URL para o registo de corretores
    path('register_corretor/', CorretorRegistrationView.as_view(), name='register_corretor'),
]
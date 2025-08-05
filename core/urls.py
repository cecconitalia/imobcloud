# C:\wamp64\www\ImobCloud\core\urls.py

from django.urls import path
# ATUALIZADO: Importar a nova view
from .views import DashboardStatsView, CorretorRegistrationView, CorretorListView

urlpatterns = [
    # URL para as estatísticas do dashboard
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    
    # URL para o registo de corretores
    path('register_corretor/', CorretorRegistrationView.as_view(), name='register_corretor'),

    # NOVO: URL para listar os corretores da imobiliária
    path('corretores/', CorretorListView.as_view(), name='lista_corretores'),
]
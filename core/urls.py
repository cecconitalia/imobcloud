# C:\wamp64\www\ImobCloud\core\urls.py

from django.urls import path
from .views import DashboardStatsView

urlpatterns = [
    # URL para as estatísticas do dashboard
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
]
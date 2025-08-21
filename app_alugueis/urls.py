# C:\wamp64\www\ImobCloud\app_alugueis\urls.py

from django.urls import path
from .views import AluguelDashboardStatsView

urlpatterns = [
    path('dashboard-stats/', AluguelDashboardStatsView.as_view(), name='aluguel-dashboard-stats'),
]
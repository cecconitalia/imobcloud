# C:\wamp64\www\imobcloud\app_alugueis\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AluguelViewSet, DashboardStatsView # CORRIGIDO: Nome da view

router = DefaultRouter()
router.register(r'alugueis', AluguelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats-alugueis'),
]
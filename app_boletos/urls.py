# C:\wamp64\www\ImobCloud\app_boletos\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConfiguracaoBancoViewSet, BoletoViewSet

router = DefaultRouter()
router.register(r'configuracoes-banco', ConfiguracaoBancoViewSet, basename='configuracoes-banco')
router.register(r'ciclo-boletos', BoletoViewSet, basename='ciclo-boletos')

urlpatterns = [
    path('', include(router.urls)),
]
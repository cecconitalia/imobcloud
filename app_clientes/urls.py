# C:\wamp64\www\ImobCloud\app_clientes\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClienteViewSet, 
    VisitaViewSet, 
    AtividadeViewSet, 
    OportunidadeViewSet,
)

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'visitas', VisitaViewSet)
router.register(r'atividades', AtividadeViewSet)
# Adicione a nova rota para o ViewSet de Oportunidades
router.register(r'oportunidades', OportunidadeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
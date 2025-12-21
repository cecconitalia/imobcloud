# cecconitalia/imobcloud/imobcloud-85e8d8db143291cf903762cada38bc23860ec7c6/app_vistorias/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VistoriaViewSet, 
    AmbienteViewSet, 
    ItemVistoriaViewSet, 
    VistoriaFotoViewSet
)

# Utilização do SimpleRouter para registrar as ViewSets e gerar automaticamente as rotas padrão (CRUD)
router = DefaultRouter()
router.register(r'vistorias', VistoriaViewSet, basename='vistoria')
router.register(r'ambientes', AmbienteViewSet, basename='ambiente')
router.register(r'itens', ItemVistoriaViewSet, basename='item-vistoria')
router.register(r'fotos', VistoriaFotoViewSet, basename='vistoria-foto')

urlpatterns = [
    # Inclui todas as rotas geradas pelo router, incluindo a nova action 'gerar-saida-da-entrada'
    path('', include(router.urls)),
]
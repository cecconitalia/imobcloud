# Em app_imoveis/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# 1. Importar a nova ViewSet
from .views import ImovelViewSet, ImagemImovelViewSet, ContatoImovelViewSet

router = DefaultRouter()
router.register(r'imoveis', ImovelViewSet)
router.register(r'imagens', ImagemImovelViewSet)
# 2. Registar o novo endpoint
router.register(r'contatos', ContatoImovelViewSet, basename='contatoimovel')

urlpatterns = [
    path('', include(router.urls)),
]
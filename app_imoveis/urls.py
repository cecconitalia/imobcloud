# Em app_imoveis/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# ATUALIZADO
from .views import ImovelViewSet, ImagemImovelViewSet, ContatoImovelViewSet

router = DefaultRouter()
router.register(r'imoveis', ImovelViewSet)
router.register(r'imagens', ImagemImovelViewSet)
# ATUALIZADO
router.register(r'contatos', ContatoImovelViewSet, basename='contatoimovel')

urlpatterns = [
    path('', include(router.urls)),
]
# app_imoveis/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImovelViewSet, ImagemImovelViewSet

router = DefaultRouter()
router.register(r'imoveis', ImovelViewSet)
router.register(r'imagens', ImagemImovelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
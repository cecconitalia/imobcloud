# config/urls_public.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importe as views das suas apps
from properties.views import PropertyViewSet
from tenants.views import TenantViewSet # <--- IMPORTE A NOVA VIEW

# O roteador agora gerencia ambas as APIs
router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'tenants', TenantViewSet, basename='tenant') # <--- REGISTRE A NOVA ROTA

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
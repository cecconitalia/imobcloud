# C:\wamp64\www\ImobCloud\app_clientes\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, VisitaViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'visitas', VisitaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
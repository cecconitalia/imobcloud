# C:\wamp64\www\ImobCloud\app_contratos\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContratoViewSet

router = DefaultRouter()
router.register(r'contratos', ContratoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
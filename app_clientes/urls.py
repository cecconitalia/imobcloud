# C:\wamp64\www\ImobCloud\app_clientes\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# Garanta que a OportunidadeViewSet está a ser importada
from .views import ClienteViewSet, VisitaViewSet, AtividadeViewSet, OportunidadeViewSet

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'visitas', VisitaViewSet)
router.register(r'atividades', AtividadeViewSet)
# Esta linha regista o endpoint que está a dar o erro 404
router.register(r'oportunidades', OportunidadeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
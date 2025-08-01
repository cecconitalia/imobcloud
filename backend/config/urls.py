# config/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from properties.views import PropertyViewSet

# Cria um roteador padrão do DRF.
router = DefaultRouter()

# Registra a nossa ViewSet de Imóveis com o roteador.
# O DRF irá gerar as URLs: /properties/, /properties/{id}/, etc.
router.register(r'properties', PropertyViewSet, basename='property')

# As URLs da nossa API são determinadas automaticamente pelo roteador.
# Nós as incluímos sob o prefixo /api/.
urlpatterns = [
    path('api/', include(router.urls)),
]
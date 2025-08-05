# C:\wamp64\www\ImobCloud\app_contratos\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# ATUALIZADO: Importar a nova ViewSet
from .views import ContratoViewSet, PagamentoViewSet

router = DefaultRouter()
router.register(r'contratos', ContratoViewSet)
# NOVO: Registar a rota para pagamentos
router.register(r'pagamentos', PagamentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
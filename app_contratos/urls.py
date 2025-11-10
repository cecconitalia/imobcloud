# C:\wamp64\www\imobcloud\app_contratos\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# ==================================================================
# CORREÇÃO: Removidas as importações que causam o crash
# (GerarReciboView, etc.)
# ==================================================================
from .views import ContratoViewSet, PagamentoViewSet

router = DefaultRouter()
router.register(r'contratos', ContratoViewSet, basename='contrato')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamento')

urlpatterns = [
    path('', include(router.urls)),
    
    # As rotas para 'gerar-recibo' e 'gerar-documento' são
    # criadas automaticamente pelo router.register
]
# C:\wamp64\www\imobcloud\app_contratos\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContratoViewSet, PagamentoViewSet, GerarReciboView

# Cria um roteador para os ViewSets
router = DefaultRouter()
router.register(r'contratos', ContratoViewSet, basename='contrato')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamento')

urlpatterns = [
    # Inclui as rotas automáticas do router (contratos/, pagamentos/)
    path('', include(router.urls)),
    
    # Rota personalizada para o recibo
    path('pagamentos/<int:pagamento_id>/recibo/', GerarReciboView.as_view(), name='gerar-recibo'),
]
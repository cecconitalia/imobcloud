# C:\wamp64\www\ImobCloud\app_contratos\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContratoViewSet, PagamentoViewSet, GerarReciboView

router = DefaultRouter()

# CORREÇÃO: Adicionado o basename para maior clareza
router.register(r'contratos', ContratoViewSet, basename='contrato')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamento')

urlpatterns = [
    path('', include(router.urls)),
    path('pagamentos/<int:pagamento_id>/recibo/', GerarReciboView.as_view(), name='gerar-recibo'),
]
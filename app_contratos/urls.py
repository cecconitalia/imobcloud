# C:\wamp64\www\ImobCloud\app_contratos\urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# ADICIONE A NOVA VIEW
from .views import ContratoViewSet, PagamentoViewSet, GerarReciboView

router = DefaultRouter()
router.register(r'contratos', ContratoViewSet)
router.register(r'pagamentos', PagamentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # NOVA ROTA PARA O RECIBO
    path('pagamentos/<int:pagamento_id>/recibo/', GerarReciboView.as_view(), name='gerar-recibo'),
]
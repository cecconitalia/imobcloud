# C:\wamp64\www\imobcloud\app_contratos\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# ==================================================================
# CORREÇÃO: Importações das views que faltavam
# ==================================================================
from .views import (
    ContratoViewSet, 
    PagamentoViewSet, 
    GerarReciboView, 
    gerar_contrato_pdf_editado
)

router = DefaultRouter()
router.register(r'contratos', ContratoViewSet, basename='contrato')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamento')

urlpatterns = [
    # Rotas do ViewSet (geradas automaticamente)
    path('', include(router.urls)),
    
    # ==================================================================
    # CORREÇÃO: Rotas manuais necessárias que estavam faltando
    # ==================================================================
    
    # Rota para a APIView de geração de recibo de pagamento
    path(
        'pagamentos/<int:pagamento_id>/gerar-recibo/', 
        GerarReciboView.as_view(), 
        name='gerar-recibo'
    ),
    
    # Rota para a @api_view de geração de PDF editado (usada pela action do frontend)
    path(
        'contratos/<int:contrato_id>/gerar-pdf-editado/', 
        gerar_contrato_pdf_editado, 
        name='gerar-contrato-pdf-editado'
    ),
]
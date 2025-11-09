# C:\wamp64\www\imobcloud\app_contratos\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContratoViewSet, PagamentoViewSet, GerarReciboView, gerar_contrato_pdf_editado # Importe a nova view de POST


# Cria um roteador para os ViewSets
router = DefaultRouter()
router.register(r'contratos', ContratoViewSet, basename='contrato')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamento')

urlpatterns = [
    # Inclui as rotas automáticas do router (incluindo a action 'gerar-financeiro' e 'pagamentos')
    path('', include(router.urls)), #
    
    # Rota personalizada para o recibo
    path('pagamentos/<int:pagamento_id>/recibo/', GerarReciboView.as_view(), name='gerar-recibo'),
    
    # Nova rota para receber o HTML editado e gerar o PDF
    path('contratos/<int:contrato_id>/gerar-pdf-editado/', gerar_contrato_pdf_editado, name='gerar-contrato-pdf-editado'),
]
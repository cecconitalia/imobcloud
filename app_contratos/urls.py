from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContratoViewSet, 
    PagamentoViewSet, 
    GerarReciboView, 
    gerar_contrato_pdf_editado, 
    limpar_estilos_view,
    ModeloContratoViewSet
)

# Cria o roteador
router = DefaultRouter()

# Registra as rotas principais
# Isso cria: /contratos/, /contratos/{id}/ e /contratos/dashboard-stats/
router.register(r'contratos', ContratoViewSet, basename='contratos')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamento')
router.register(r'modelos-contrato', ModeloContratoViewSet, basename='modelo-contrato')

urlpatterns = [
    # Rota explícita para Dashboard Stats para evitar 404 em alguns casos de roteamento
    path('contratos/dashboard-stats/', ContratoViewSet.as_view({'get': 'dashboard_stats'}), name='contratos-dashboard-stats'),

    # Inclui as rotas automáticas do router
    path('', include(router.urls)),
    
    # Rotas Manuais (Ações específicas)
    path('recibo/<int:pagamento_id>/gerar/', GerarReciboView.as_view(), name='gerar_recibo_pdf'),
    path('contratos/<int:pk>/gerar-pdf-editado/', gerar_contrato_pdf_editado, name='gerar_contrato_pdf_editado'), 
    path('contratos/<int:pk>/limpar-estilos/', limpar_estilos_view, name='limpar_estilos'),
]
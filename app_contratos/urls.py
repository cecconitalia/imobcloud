# Em app_contratos/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContratoViewSet, PagamentoViewSet, GerarReciboView, 
    gerar_contrato_pdf_editado, limpar_estilos_view,
    # ==========================================================
    # === IMPORTAÇÃO ADICIONADA: ModeloContratoViewSet       ===
    # ==========================================================
    ModeloContratoViewSet
)

router = DefaultRouter()
router.register(r'contratos', ContratoViewSet, basename='contrato')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamento')

# ==========================================================
# === NOVO REGISTRO: API para Modelos de Contrato        ===
# ==========================================================
router.register(r'modelos-contrato', ModeloContratoViewSet, basename='modelo-contrato')
# ==========================================================


urlpatterns = [
    path('', include(router.urls)),
    
    # URLs de Ação (mantidas)
    path('recibo/<int:pagamento_id>/gerar/', GerarReciboView.as_view(), name='gerar_recibo_pdf'),
    
    # (Esta URL agora é redundante, mas mantida por segurança)
    path('contratos/<int:pk>/gerar-pdf-editado/', gerar_contrato_pdf_editado, name='gerar_contrato_pdf_editado'), 
    
    path('contratos/<int:pk>/limpar-estilos/', limpar_estilos_view, name='limpar_estilos'),
]
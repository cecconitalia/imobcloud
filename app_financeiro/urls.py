from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ContaBancariaViewSet, TransacaoViewSet, FormaPagamentoViewSet

# O router é a única fonte de verdade para as URLs do ModelViewSet
router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'contas', ContaBancariaViewSet)
router.register(r'transacoes', TransacaoViewSet)
router.register(r'formas-pagamento', FormaPagamentoViewSet) # NOVO: Registamos o ViewSet das formas de pagamento

urlpatterns = [
    # Apenas inclui as URLs geradas pelo router
    path('', include(router.urls)),

    # Adicione as URLs personalizadas como actions do ViewSet
    # Isso garante que o roteador principal não entre em conflito
    # com as rotas que terminam em "transacoes/"
    path('transacoes/stats/', TransacaoViewSet.as_view({'get': 'stats'}), name='stats-report'),
    path('transacoes/dre/', TransacaoViewSet.as_view({'get': 'dre'}), name='dre-report'),
]
# C:\wamp64\www\ImobCloud\app_financeiro\urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ContaViewSet, TransacaoViewSet, FormaPagamentoViewSet, DREViewAPI

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'contas', ContaViewSet)
router.register(r'transacoes', TransacaoViewSet)
router.register(r'formas-pagamento', FormaPagamentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # ADICIONADO: Rota para o Relatório DRE
    path('dre/', DREViewAPI.as_view(), name='dre_report'),
]
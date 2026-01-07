# app_financeiro/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransacaoViewSet, CategoriaViewSet, ContaViewSet, FormaPagamentoViewSet, DREViewAPI

router = DefaultRouter()
router.register(r'transacoes', TransacaoViewSet) # Isso gera as rotas automáticas, incluindo 'ranking-imoveis'
router.register(r'categorias', CategoriaViewSet)
router.register(r'contas', ContaViewSet)
router.register(r'formas-pagamento', FormaPagamentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dre/', DREViewAPI.as_view(), name='dre-api'),
]
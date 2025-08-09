from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ContaBancariaViewSet, TransacaoViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet)
router.register(r'contas-bancarias', ContaBancariaViewSet)
router.register(r'transacoes', TransacaoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', TransacaoViewSet.as_view({'get': 'stats'}), name='stats-report'),
    path('dre/', TransacaoViewSet.as_view({'get': 'dre'}), name='dre-report'),
]
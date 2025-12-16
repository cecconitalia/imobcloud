from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VistoriaViewSet, AmbienteViewSet, ItemVistoriaViewSet, VistoriaFotoViewSet

router = DefaultRouter()
router.register(r'vistorias', VistoriaViewSet, basename='vistorias')
router.register(r'ambientes', AmbienteViewSet, basename='ambientes')
router.register(r'itens', ItemVistoriaViewSet, basename='itens')
router.register(r'fotos', VistoriaFotoViewSet, basename='fotos')

urlpatterns = [
    path('', include(router.urls)),
    # Rota explícita para garantir o funcionamento do upload customizado
    path('fotos/upload-lote/', VistoriaFotoViewSet.as_view({'post': 'upload_lote'}), name='fotos-upload-lote'),
]
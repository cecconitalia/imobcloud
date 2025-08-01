from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Importe as views das suas apps
from properties.views import PropertyViewSet
from tenants.views import TenantViewSet
from users.views import UserViewSet # Adicione a importação do UserViewSet para a API

# O roteador gerencia os endpoints da API para propriedades e inquilinos
router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'users', UserViewSet, basename='user') # Adicione o UserViewSet para gerenciar usuários

urlpatterns = [
    # Redireciona a raiz para o admin
    path('', RedirectView.as_view(url='admin/', permanent=False), name='root_redirect'),
    path('admin/', admin.site.urls),

    # --- ENDPOINTS DE AUTENTICAÇÃO JWT ---
    # Adicione estes caminhos para permitir que o frontend obtenha e atualize tokens
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- OUTROS ENDPOINTS DA API PÚBLICA ---
    path('api/', include(router.urls)),
]

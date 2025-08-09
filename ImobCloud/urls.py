from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importe apenas a view de token personalizada aqui
from core.views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Endpoints de cada app da sua API
    path('api/v1/imoveis/', include('app_imoveis.urls')),
    path('api/v1/clientes/', include('app_clientes.urls')),
    path('api/v1/contratos/', include('app_contratos.urls')),
    path('api/v1/core/', include('core.urls')),
    # ADICIONADO: URL do novo módulo financeiro
    path('api/v1/financeiro/', include('app_financeiro.urls')),

    # A linha abaixo usa a sua view personalizada para o login
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Endpoint para atualizar o token
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Adiciona os URLs de login/logout para a interface da API no navegador
    path('api-auth/', include('rest_framework.urls'))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
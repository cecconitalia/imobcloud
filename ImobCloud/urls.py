# ImobCloud/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Importe settings
from django.conf.urls.static import static # Importe static para servir arquivos

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # APIs RESTful versionadas (v1)
    path('api/v1/imoveis/', include('app_imoveis.urls')),
    path('api/v1/clientes/', include('app_clientes.urls')),
    path('api/v1/contratos/', include('app_contratos.urls')),

    # URLs para autenticação JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # URLs do nosso app 'core' para o perfil do usuário
    path('api/v1/core/', include('core.urls')),
]

# NOVO: Configuração para servir arquivos de mídia em ambiente de desenvolvimento
if settings.DEBUG: # Isso só funciona se DEBUG=True
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
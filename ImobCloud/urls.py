# Em ImobCloud/urls.py

from django.contrib import admin
from django.urls import path, include
# ADIÇÃO DAS DUAS IMPORTAÇÕES NECESSÁRIAS
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

# Importações principais do seu app 'core'
from core.views import MyTokenObtainPairView, LogoutView

# Views públicas que não precisam de autenticação de tenant no mesmo nível da API
from app_imoveis.views import ImovelPublicListView, ImovelPublicDetailView

urlpatterns = [
    # Rota de administração do Django
    path('admin/', admin.site.urls),

    # --- ROTAS PÚBLICAS (para o site de cada imobiliária) ---
    path('public/imoveis/', ImovelPublicListView.as_view(), name='imovel-public-list'),
    path('public/imoveis/<int:pk>/', ImovelPublicDetailView.as_view(), name='imovel-public-detail'),
    
    # --- ROTAS DA API (para o painel de gestão) ---
    path('api/v1/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/logout/', LogoutView.as_view(), name='auth_logout'),
    
    # --- Inclusão das rotas de cada app da API (MÉTODO CORRIGIDO) ---
    path('api/v1/', include('core.urls')),
    path('api/v1/', include('app_imoveis.urls')),
    path('api/v1/', include('app_clientes.urls')),
    path('api/v1/', include('app_contratos.urls')),
    path('api/v1/financeiro/', include('app_financeiro.urls')),
    path('api/v1/alugueis/', include('app_alugueis.urls')),
    path('api/v1/boletos/', include('app_boletos.urls')),
    
    # Rota corrigida para a app de publicações
    path('api/v1/publicacoes/', include('app_publicacoes.urls')),
    
    # Rota para a app de configuração da IA
    path('api/v1/configuracao-ia/', include('app_config_ia.urls')),
    
    # Rota para autenticação de sessão da DRF (útil para o browsable API)
    path('api-auth/', include('rest_framework.urls')),
]

# ADICIONE ESTE BLOCO DE CÓDIGO NO FINAL DO ARQUIVO
# Ele serve os arquivos de mídia (uploads) apenas em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# C:\wamp64\www\ImobCloud\ImobCloud\urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

# Importações principais do seu app 'core'
from core.views import MyTokenObtainPairView, LogoutView

# Views públicas
from app_imoveis.views import ImovelPublicListView, ImovelPublicDetailView, ImobiliariaPublicDetailView, ImovelIAView, ContatoImovelViewSet

urlpatterns = [
    # Rota de administração do Django
    path('admin/', admin.site.urls),

    # --- ROTAS PÚBLICAS (Sem Prefixos API) ---
    path('public/imoveis/', ImovelPublicListView.as_view(), name='imovel-public-list'),
    path('public/imoveis/<int:pk>/', ImovelPublicDetailView.as_view(), name='imovel-public-detail'),
    path('public/imobiliaria/<str:pk>/', ImobiliariaPublicDetailView.as_view(), name='imobiliaria-public-detail'),
    path('public/imoveis/busca-ia/', ImovelIAView.as_view(), name='imovel-busca-ia'),
    path('public/contatos/', ContatoImovelViewSet.as_view({'post': 'create'}), name='contato-public-create'),

    # --- ROTAS DA API (Para o painel de gestão) ---
    path('api/v1/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/logout/', LogoutView.as_view(), name='auth_logout'),
    
    # --- Inclusão das rotas de cada app da API ---
    path('api/v1/', include('core.urls')),
    
    # Prefixos corrigidos para casar com o Frontend
    path('api/v1/', include('app_imoveis.urls')), 
    path('api/v1/', include('app_clientes.urls')),
    
    # --- CORREÇÃO AQUI: Adicionado 'contratos/' para formar /api/v1/contratos/contratos/ ---
    path('api/v1/', include('app_contratos.urls')),

    
    path('api/v1/financeiro/', include('app_financeiro.urls')),
    path('api/v1/alugueis/', include('app_alugueis.urls')),
    path('api/v1/boletos/', include('app_boletos.urls')),
    path('api/v1/vistorias/', include('app_vistorias.urls')),
    path('api/v1/publicacoes/', include('app_publicacoes.urls')),
    path('api/v1/configuracao-ia/', include('app_config_ia.urls')),
    
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.static import serve

from rest_framework_simplejwt.views import TokenRefreshView
from core.views import CustomTokenObtainPairView, LogoutView, DashboardStatsView

from app_imoveis.views import (
    ImovelPublicListView,
    ImovelPublicDetailView,
    ImobiliariaPublicDetailView,
    ImovelIAView,
    ContatoImovelViewSet
)

# =============================================================
# VIEW PRINCIPAL DO FRONTEND
# =============================================================
@ensure_csrf_cookie
def index_view(request):
    """
    Renderiza o index.html do build do Vue.js.
    O Django procura este arquivo nas pastas definidas em TEMPLATES['DIRS'].
    """
    return render(request, 'index.html')

urlpatterns = [
    # =========================================================
    # ADMIN
    # =========================================================
    path('admin/', admin.site.urls),

    # =========================================================
    # ROTAS PÚBLICAS (BACKEND)
    # =========================================================
    path('public/imoveis/', ImovelPublicListView.as_view(), name='imovel-public-list'),
    path('public/imoveis/<int:pk>/', ImovelPublicDetailView.as_view(), name='imovel-public-detail'),
    path('public/imobiliaria/<str:pk>/', ImobiliariaPublicDetailView.as_view(), name='imobiliaria-public-detail'),
    path('public/imoveis/busca-ia/', ImovelIAView.as_view(), name='imovel-busca-ia'),
    path('public/contatos/', ContatoImovelViewSet.as_view({'post': 'create'}), name='contato-public-create'),

    # =========================================================
    # API
    # =========================================================
    path('api/v1/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/logout/', LogoutView.as_view(), name='auth_logout'),
    path('api/v1/stats/', DashboardStatsView.as_view(), name='dashboard_stats_root'),

    path('api/v1/core/', include('core.urls')),
    path('api/v1/', include('app_imoveis.urls')),
    path('api/v1/', include('app_clientes.urls')),
    path('api/v1/', include('app_contratos.urls')),
    path('api/v1/financeiro/', include('app_financeiro.urls')),
    path('api/v1/alugueis/', include('app_alugueis.urls')),
    path('api/v1/boletos/', include('app_boletos.urls')),
    path('api/v1/vistorias/', include('app_vistorias.urls')),
    path('api/v1/publicacoes/', include('app_publicacoes.urls')),
    path('api/v1/configuracao-ia/', include('app_config_ia.urls')),

    path('api-auth/', include('rest_framework.urls')),
]

# =============================================================
# FRONTEND E ARQUIVOS ESTÁTICOS
# ⚠️ ORDEM IMPORTANTE: 
# 1. Assets físicos primeiro
# 2. Rota raiz exata
# 3. Media (se debug)
# 4. Catch-all por último
# =============================================================

# Servir arquivos de assets do Vue diretamente por aqui se o WhiteNoise falhar
urlpatterns += [
    re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'frontend/dist/assets')}),
]

# Rota raiz exata (Home)
urlpatterns += [
    path('', index_view, name='index'),
]

# Media (Imagens de upload)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# REGRA CATCH-ALL (Vue Router)
# Redireciona qualquer URL que não comece com palavras reservadas para o index.html
urlpatterns += [
    re_path(r'^(?!api|admin|static|media|assets|favicon.ico).*$', index_view, name='vue_catch_all'),
]
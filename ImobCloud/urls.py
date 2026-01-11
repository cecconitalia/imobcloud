import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import logout

# Views de Autenticação e API
from rest_framework_simplejwt.views import TokenRefreshView
from core.views import CustomTokenObtainPairView, LogoutView, DashboardStatsView

# Views Públicas
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
    """
    return render(request, 'index.html')

def custom_admin_logout(request):
    """
    Força o logout do admin via GET para corrigir compatibilidade 
    entre Django 5+ e temas como Jazzmin.
    """
    logout(request)
    return redirect('/admin/login/')

urlpatterns = [
    # =========================================================
    # CORREÇÃO DE LOGOUT DO ADMIN
    # =========================================================
    # Esta rota deve vir ANTES de admin.site.urls para sobrescrever o padrão
    path('admin/logout/', custom_admin_logout, name='admin_logout_fix'),

    # =========================================================
    # ADMIN
    # =========================================================
    path('admin/', admin.site.urls),

    # =========================================================
    # ROTAS PÚBLICAS E API
    # =========================================================
    path('public/imoveis/', ImovelPublicListView.as_view(), name='imovel-public-list'),
    path('public/imoveis/<int:pk>/', ImovelPublicDetailView.as_view(), name='imovel-public-detail'),
    path('public/imobiliaria/<str:pk>/', ImobiliariaPublicDetailView.as_view(), name='imobiliaria-public-detail'),
    path('public/imoveis/busca-ia/', ImovelIAView.as_view(), name='imovel-busca-ia'),
    path('public/contatos/', ContatoImovelViewSet.as_view({'post': 'create'}), name='contato-public-create'),

    path('api/v1/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/logout/', LogoutView.as_view(), name='auth_logout'),
    path('api/v1/stats/', DashboardStatsView.as_view(), name='dashboard_stats_root'),

    # Includes dos Apps
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
# =============================================================

# Configura arquivos de Mídia (Uploads) apenas em DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Adiciona rota estática explícita para garantir carregamento local se Whitenoise falhar em DEV
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'frontend', 'dist'))

# Rota raiz exata (Home)
urlpatterns += [
    path('', index_view, name='index'),
]

# Regra Catch-All (Vue Router)
# Redireciona qualquer URL não encontrada para o index.html, 
# EXCETO se começar com /static, /media, /api ou /admin
urlpatterns += [
    re_path(r'^(?!api|admin|static|media|favicon.ico).*$', index_view, name='vue_catch_all'),
]
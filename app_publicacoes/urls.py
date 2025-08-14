# app_publicacoes/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GerarTextoPublicacaoView,
    PublicacaoRedeSocialView,
    AgendarPublicacaoView,
    CalendarioPublicacoesView,
    PostAgendadoViewSet # <--- 1. IMPORTE O NOVO VIEWSET
)

# Cria um router e regista o nosso ViewSet
router = DefaultRouter()
router.register(r'posts-agendados', PostAgendadoViewSet, basename='postagendado')

urlpatterns = [
    # Rotas existentes
    path('gerar-texto/', GerarTextoPublicacaoView.as_view(), name='gerar-texto-publicacao'),
    path('publicar/', PublicacaoRedeSocialView.as_view(), name='publicar-rede-social'),
    path('agendar/', AgendarPublicacaoView.as_view(), name='agendar-publicacao'),
    path('calendario/', CalendarioPublicacoesView.as_view(), name='calendario-publicacoes'),

    # --- 2. ADICIONE AS ROTAS DO ROUTER ---
    # Isto cria automaticamente as rotas:
    # GET /posts-agendados/ (listar)
    # GET /posts-agendados/{id}/ (detalhe)
    # PUT/PATCH /posts-agendados/{id}/ (atualizar)
    # DELETE /posts-agendados/{id}/ (excluir)
    path('', include(router.urls)),
]
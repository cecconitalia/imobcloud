# app_publicacoes/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from app_imoveis.views import ImovelViewSet
from .views import (
    GerarTextoPublicacaoView,
    PublicacaoRedeSocialView,
    AgendarPublicacaoView,
    CalendarioPublicacoesView,
    PostAgendadoViewSet,
    PublicacaoHistoricoViewSet
)

# Cria o router principal da app de publicações
router = DefaultRouter()
router.register(r'imoveis', ImovelViewSet, basename='imovel')
router.register(r'posts-agendados', PostAgendadoViewSet, basename='postagendado')

# Roteador aninhado para o histórico de publicações
imoveis_router = routers.NestedSimpleRouter(router, r'imoveis', lookup='imovel')
imoveis_router.register(r'historico', PublicacaoHistoricoViewSet, basename='imovel-historico')

urlpatterns = [
    # Rotas baseadas em APIView
    path('gerar-texto/', GerarTextoPublicacaoView.as_view(), name='gerar-texto-publicacao'),
    path('publicar/', PublicacaoRedeSocialView.as_view(), name='publicar-rede-social'),
    path('agendar/', AgendarPublicacaoView.as_view(), name='agendar-publicacao'),
    path('calendario/', CalendarioPublicacoesView.as_view(), name='calendario-publicacoes'),

    # Rotas de ViewSets
    path('', include(router.urls)),
    path('', include(imoveis_router.urls)),
]
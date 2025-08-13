# app_publicacoes/urls.py

from django.urls import path
from .views import (
    GerarTextoPublicacaoView,
    PublicacaoRedeSocialView,
    AgendarPublicacaoView,
    CalendarioPublicacoesView
)

urlpatterns = [
    # Esta linha regista a rota para a sua view de IA
    path('gerar-texto/', GerarTextoPublicacaoView.as_view(), name='gerar-texto-publicacao'),
    
    # Esta linha regista a rota para a publicação efetiva nas redes sociais
    path('publicar/', PublicacaoRedeSocialView.as_view(), name='publicar-rede-social'),

    # NOVA ROTA DE AGENDAMENTO ---
    path('agendar/', AgendarPublicacaoView.as_view(), name='agendar-publicacao'),
    
    # ROTA DO CALENDÁRIO
    path('calendario/', CalendarioPublicacoesView.as_view(), name='calendario-publicacoes'),


]
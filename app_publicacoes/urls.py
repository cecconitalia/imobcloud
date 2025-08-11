# app_publicacoes/urls.py

from django.urls import path
# ATUALIZADO: Importe a nova View
from .views import GerarTextoPublicacaoView, PublicarPostView 

urlpatterns = [
    # Rota existente para gerar o texto
    path('gerar-texto/', GerarTextoPublicacaoView.as_view(), name='gerar_texto_publicacao'),

    # NOVA ROTA: Adicione esta linha para a publicação
    path('publicar/', PublicarPostView.as_view(), name='publicar_post'),
]
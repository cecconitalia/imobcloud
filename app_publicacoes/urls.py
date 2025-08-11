# C:\wamp64\www\imobcloud\app_publicacoes\urls.py

from django.urls import path
# Importamos a view com o nome novo que criamos: PublicacaoRedeSocialView
from .views import GerarTextoPublicacaoView, PublicacaoRedeSocialView

urlpatterns = [
    path('gerar-texto/', GerarTextoPublicacaoView.as_view(), name='gerar_texto_publicacao'),
    # E usamos o nome novo da view aqui também
    path('publicar/', PublicacaoRedeSocialView.as_view(), name='publicar_rede_social'),
]
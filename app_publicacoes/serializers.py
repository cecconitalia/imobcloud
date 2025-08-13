# app_publicacoes/serializers.py

from rest_framework import serializers
from .models import PostAgendado

class PostAgendadoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo PostAgendado, formatado para ser
    consumido por um calendário no frontend.
    """
    # Renomeamos os campos para os nomes que a maioria das bibliotecas de calendário espera
    title = serializers.CharField(source='imovel.titulo_anuncio')
    start = serializers.DateTimeField(source='data_agendamento')

    class Meta:
        model = PostAgendado
        fields = [
            'id',
            'title',       # Título do evento (nome do imóvel)
            'start',       # Data de início do evento (data de agendamento)
            'status',      # Status para podermos colorir o evento
            'texto',       # O texto do post para visualização
            'plataformas', # As plataformas
            'resultado_publicacao' # O resultado para vermos os erros
        ]
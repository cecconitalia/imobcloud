# app_publicacoes/serializers.py

from rest_framework import serializers
from .models import PostAgendado
from .models import PublicacaoHistorico, PublicacaoSocial


class PostAgendadoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo PostAgendado.
    Usado tanto para o calendário quanto para as operações de CRUD (Criar, Ler, Atualizar, Excluir).
    """
    # Campos para exibição no calendário (read-only)
    title = serializers.CharField(source='imovel.titulo_anuncio', read_only=True)
    start = serializers.DateTimeField(source='data_agendamento', read_only=True)

    class Meta:
        model = PostAgendado
        # Lista completa de campos
        fields = [
            'id',
            'imovel',
            'title',       # Título do evento (nome do imóvel)
            'start',       # Data de início do evento (data de agendamento)
            'status',
            'texto',
            'plataformas',
            'data_agendamento', # Campo editável
            'resultado_publicacao'
        ]
        # Campos que não podem ser editados diretamente pelo cliente,
        # mas são necessários para a lógica interna ou exibição.
        read_only_fields = [
            'status',
            'imovel',
            'resultado_publicacao'
        ]

class PublicacaoHistoricoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicacaoHistorico
        fields = '__all__'
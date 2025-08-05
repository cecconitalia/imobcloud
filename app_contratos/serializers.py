# C:\wamp64\www\ImobCloud\app_contratos\serializers.py
from rest_framework import serializers
from .models import Contrato, Pagamento
from app_imoveis.serializers import ImovelDisplaySerializer
from app_clientes.serializers import ClienteDisplaySerializer

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'
        read_only_fields = ('contrato',)


# Serializer para AÇÕES DE ESCRITA (Criar e Atualizar)
class ContratoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        # Apenas os campos que esperamos receber do frontend
        fields = [
            'imovel', 'cliente', 'tipo_contrato', 'data_inicio', 'data_fim',
            'data_assinatura', 'valor_total', 'condicoes_pagamento', 'status_contrato'
        ]


# Serializer para a LISTA de contratos (Leitura)
class ContratoListSerializer(serializers.ModelSerializer):
    imovel_obj = ImovelDisplaySerializer(source='imovel', read_only=True)
    cliente_obj = ClienteDisplaySerializer(source='cliente', read_only=True)

    class Meta:
        model = Contrato
        fields = [
            'id', 'imovel_obj', 'cliente_obj', 'tipo_contrato', 'status_contrato'
        ]


# Serializer para os DETALHES de um contrato (Leitura)
class ContratoDetailSerializer(serializers.ModelSerializer):
    imovel_obj = ImovelDisplaySerializer(source='imovel', read_only=True)
    cliente_obj = ClienteDisplaySerializer(source='cliente', read_only=True)
    pagamentos = PagamentoSerializer(many=True, read_only=True)

    class Meta:
        model = Contrato
        fields = '__all__' # Inclui todos os campos do modelo + os de cima
        read_only_fields = ('imobiliaria',)
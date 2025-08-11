# app_financeiro/serializers.py

from rest_framework import serializers
from .models import Categoria, ContaBancaria, Transacao

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        exclude = ['imobiliaria']

class ContaBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaBancaria
        exclude = ['imobiliaria']

# --- SERIALIZER DE TRANSAÇÃO TOTALMENTE ATUALIZADO ---
class TransacaoSerializer(serializers.ModelSerializer):
    # Campos que retornam o nome dos objetos relacionados (apenas para leitura)
    categoria_nome = serializers.StringRelatedField(source='categoria.nome', read_only=True)
    conta_bancaria_nome = serializers.StringRelatedField(source='conta_bancaria.nome', read_only=True)

    class Meta:
        model = Transacao
        # Lista explícita de todos os campos que a API vai usar
        fields = [
            'id', 
            'descricao', 
            'valor', 
            'tipo',
            'data_vencimento', 
            'data_pagamento', 
            'status', 
            'categoria', 
            'conta_bancaria', 
            'imovel',
            'contrato',
            # Campos 'read-only' que ajudam o frontend
            'categoria_nome',
            'conta_bancaria_nome'
        ]
        # Garante que campos de relacionamento sejam opcionais na escrita
        extra_kwargs = {
            'categoria': {'required': False, 'allow_null': True},
            'imovel': {'required': False, 'allow_null': True},
            'contrato': {'required': False, 'allow_null': True},
            'data_pagamento': {'required': False, 'allow_null': True},
        }
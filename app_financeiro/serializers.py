# C:\wamp64\www\imobcloud\app_financeiro\serializers.py

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

class TransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        # CORREÇÃO: Adicionado 'imovel' à lista de campos, que será opcional na entrada
        fields = ['id', 'data', 'valor', 'descricao', 'tipo', 'categoria', 'conta_bancaria', 'imovel']
# C:\wamp64\www\ImobCloud\app_financeiro\serializers.py

from rest_framework import serializers
from .models import Categoria, Conta, Transacao, FormaPagamento
from app_clientes.models import Cliente
from app_imoveis.models import Imovel

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ('imobiliaria',)

class ContaSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Conta
        fields = '__all__'
        read_only_fields = ('imobiliaria',)

class FormaPagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPagamento
        fields = '__all__'
        read_only_fields = ('imobiliaria',)

class TransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = '__all__'
        read_only_fields = ('imobiliaria',)

class ClienteSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome_completo']

class ImovelSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imovel
        # CORREÇÃO: Trocado 'titulo' por 'titulo_anuncio'
        fields = ['id', 'titulo_anuncio']

class TransacaoListSerializer(serializers.ModelSerializer):
    categoria = serializers.StringRelatedField()
    conta = serializers.StringRelatedField()
    forma_pagamento = serializers.StringRelatedField()
    cliente = ClienteSimplificadoSerializer()
    imovel = ImovelSimplificadoSerializer()
    
    class Meta:
        model = Transacao
        fields = [
            'id', 'descricao', 'valor', 'data_transacao', 'data_vencimento',
            'tipo', 'status', 'categoria', 'conta', 'forma_pagamento',
            'cliente', 'imovel'
        ]
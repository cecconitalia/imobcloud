from rest_framework import serializers
from .models import Categoria, ContaBancaria, Transacao

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ContaBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaBancaria
        fields = ['id', 'nome', 'banco', 'agencia', 'numero_conta', 'saldo_inicial', 'saldo_atual', 'ativo'] # Alterado para incluir os novos campos

class TransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = '__all__'
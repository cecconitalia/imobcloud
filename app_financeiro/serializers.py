from rest_framework import serializers
from .models import Categoria, ContaBancaria, Transacao

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ContaBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaBancaria
        # NOVO: Excluímos o campo 'imobiliaria' para que o serializador não o espere na entrada de dados.
        # A imobiliária será injetada automaticamente pela view.
        exclude = ['imobiliaria']

class TransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = '__all__'
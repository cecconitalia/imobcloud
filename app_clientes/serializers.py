# C:\wamp64\www\ImobCloud\app_clientes\serializers.py
from rest_framework import serializers
from .models import Cliente, Visita
# Precisamos importar o Serializer do Imóvel para Visitas
from app_imoveis.serializers import ImovelDisplaySerializer # Importar o novo serializer de Imóvel

# NOVO: Serializer simplificado para exibir cliente em outras associações
class ClienteDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome_completo', 'cpf_cnpj'] # Campos que queremos exibir

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ('imobiliaria',)

# ATUALIZADO: VisitaSerializer
class VisitaSerializer(serializers.ModelSerializer):
    # Usando Serializers aninhados read_only para exibir os dados humanizados
    imovel_obj = ImovelDisplaySerializer(source='imovel', read_only=True)
    cliente_obj = ClienteDisplaySerializer(source='cliente', read_only=True)

    class Meta:
        model = Visita
        fields = '__all__'
        read_only_fields = ('imobiliaria',) # Garante que a imobiliária é definida pelo middleware
        # Adiciona os novos campos humanizados ao retorno da API
        extra_fields = ['imovel_obj', 'cliente_obj']
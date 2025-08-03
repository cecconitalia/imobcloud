# C:\wamp64\www\ImobCloud\app_contratos\serializers.py
from rest_framework import serializers
from .models import Contrato
# Precisamos importar os Serializers de Imóvel e Cliente
from app_imoveis.serializers import ImovelDisplaySerializer
from app_clientes.serializers import ClienteDisplaySerializer

# ATUALIZADO: ContratoSerializer
class ContratoSerializer(serializers.ModelSerializer):
    # Usando Serializers aninhados read_only para exibir os dados humanizados
    imovel_obj = ImovelDisplaySerializer(source='imovel', read_only=True)
    cliente_obj = ClienteDisplaySerializer(source='cliente', read_only=True)

    class Meta:
        model = Contrato
        fields = '__all__'
        read_only_fields = ('imobiliaria',) # Garante que a imobiliária é definida pelo middleware
        # Adiciona os novos campos humanizados ao retorno da API
        extra_fields = ['imovel_obj', 'cliente_obj']
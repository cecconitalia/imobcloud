# C:\wamp64\www\ImobCloud\app_contratos\serializers.py
from rest_framework import serializers
from .models import Contrato, Pagamento
# ATUALIZADO: Corrigido o nome do serializer importado
from app_imoveis.serializers import ImovelSerializer 
from app_clientes.serializers import ClienteSerializer

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'

class ContratoListSerializer(serializers.ModelSerializer):
    imovel = serializers.StringRelatedField()
    cliente = serializers.StringRelatedField()
    
    class Meta:
        model = Contrato
        fields = ['id', 'imovel', 'cliente', 'tipo_contrato', 'data_inicio', 'status_contrato']


class ContratoDetailSerializer(serializers.ModelSerializer):
    # Usando os serializers completos para exibir detalhes
    imovel = ImovelSerializer(read_only=True)
    cliente = ClienteSerializer(read_only=True)
    pagamentos = PagamentoSerializer(many=True, read_only=True)

    class Meta:
        model = Contrato
        fields = '__all__'


class ContratoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        # Exclui campos que são preenchidos automaticamente ou por lógica interna
        exclude = ['imobiliaria']
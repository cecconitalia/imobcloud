# C:\wamp64\www\ImobCloud\app_boletos\serializers.py

from rest_framework import serializers
from .models import Boleto, ConfiguracaoBanco
from app_financeiro.models import Transacao

class ConfiguracaoBancoSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo ConfiguracaoBanco.
    """
    class Meta:
        model = ConfiguracaoBanco
        fields = ['id', 'nome_banco']


class BoletoSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo Boleto.
    """
    class Meta:
        model = Boleto
        fields = '__all__'
        read_only_fields = ['imobiliaria', 'configuracao', 'status', 'data_emissao']

class GerarBoletoRequestSerializer(serializers.Serializer):
    """
    Serializador para validar os dados da requisição de geração de boleto.
    """
    transacao_id = serializers.IntegerField(
        required=True,
        help_text="ID da transação para a qual o boleto será gerado."
    )
    banco_id = serializers.IntegerField(
        required=True,
        help_text="ID da configuração de banco a ser utilizada."
    )
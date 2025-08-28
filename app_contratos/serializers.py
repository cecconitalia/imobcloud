# C:\wamp64\www\imobcloud\app_contratos\serializers.py

from rest_framework import serializers
from .models import Contrato, Pagamento
from app_imoveis.models import Imovel
from app_alugueis.models import Aluguel

class ImovelSimplificadoSerializer(serializers.ModelSerializer):
    # Campo personalizado para o endereço completo
    endereco_completo = serializers.SerializerMethodField()

    class Meta:
        model = Imovel
        # Removido 'endereco' e adicionado 'endereco_completo'
        fields = ['id', 'titulo_anuncio', 'endereco_completo']

    def get_endereco_completo(self, obj):
        """
        Gera o endereço completo a partir dos novos campos do modelo Imovel.
        """
        partes = [
            obj.logradouro,
            obj.numero,
            obj.complemento,
            obj.bairro,
            obj.cidade,
            obj.estado,
        ]
        # Filtra partes vazias e junta com vírgula
        endereco = ', '.join(filter(None, partes))
        return endereco or "Endereço não disponível"

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'

class ContratoSerializer(serializers.ModelSerializer):
    imovel = ImovelSimplificadoSerializer(read_only=True)
    pagamentos = PagamentoSerializer(many=True, read_only=True)

    class Meta:
        model = Contrato
        fields = '__all__'

class ContratoCriacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = '__all__'
# C:\wamp64\www\imobcloud\app_contratos\serializers.py

from rest_framework import serializers
from .models import Contrato, Pagamento
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from django.db import transaction

class ImovelSimplificadoSerializer(serializers.ModelSerializer):
    # Campo personalizado para o endereço completo
    endereco_completo = serializers.SerializerMethodField()

    class Meta:
        model = Imovel
        # Removido 'endereco' e adicionado 'endereco_completo'
        fields = ['id', 'titulo_anuncio', 'logradouro', 'endereco_completo']

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

class ClienteSimplificadoSerializer(serializers.ModelSerializer):
    """ Serializer simplificado para ser usado em outras entidades. """
    class Meta:
        model = Cliente
        fields = ['id', 'nome_completo']

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'

class ContratoSerializer(serializers.ModelSerializer):
    imovel = ImovelSimplificadoSerializer(read_only=True)
    pagamentos = PagamentoSerializer(many=True, read_only=True)
    
    # Adicionamos os serializers para os clientes, garantindo que os objetos completos sejam retornados
    inquilino = ClienteSimplificadoSerializer(read_only=True)
    proprietario = ClienteSimplificadoSerializer(read_only=True)

    # Campos de escrita para receber os IDs na criação/edição
    inquilino_id = serializers.PrimaryKeyRelatedField(
        source='inquilino',
        queryset=Cliente.objects.all(),
        write_only=True,
        required=True
    )
    proprietario_id = serializers.PrimaryKeyRelatedField(
        source='proprietario',
        queryset=Cliente.objects.all(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Contrato
        fields = [
            'id', 'imobiliaria', 'tipo_contrato', 'imovel', 'inquilino', 'proprietario',
            'valor_total', 'informacoes_adicionais', 'duracao_meses', 'status_contrato',
            'data_inicio', 'data_fim', 'data_assinatura', 'data_cadastro',
            'pagamentos', 'inquilino_id', 'proprietario_id', 'conteudo_personalizado' # Novo campo
        ]
        read_only_fields = ('data_cadastro',)

class ContratoCriacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = '__all__'
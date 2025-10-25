# C:\wamp64\www\imobcloud\app_contratos\serializers.py

from rest_framework import serializers
from .models import Contrato, Pagamento
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from django.db import transaction

class ImovelSimplificadoSerializer(serializers.ModelSerializer):
    endereco_completo = serializers.SerializerMethodField()

    class Meta:
        model = Imovel
        fields = ['id', 'titulo_anuncio', 'logradouro', 'endereco_completo']

    def get_endereco_completo(self, obj):
        partes = [
            obj.logradouro,
            obj.numero,
            obj.complemento,
            obj.bairro,
            obj.cidade,
            obj.estado,
        ]
        endereco = ', '.join(filter(None, partes))
        return endereco or "Endereço não disponível"

class ClienteSimplificadoSerializer(serializers.ModelSerializer):
    """ Serializer simplificado que exibe o nome correto do cliente (Físico ou Jurídico). """
    # CORRIGIDO E MELHORADO: Usa um SerializerMethodField para exibir o nome correto.
    nome_display = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        # CORRIGIDO: Substituído 'nome_completo' por 'nome_display'.
        fields = ['id', 'nome_display']

    def get_nome_display(self, obj):
        """ Retorna Razão Social para PJ, ou Nome para PF. """
        if obj.tipo_pessoa == 'JURIDICA' and obj.razao_social:
            return obj.razao_social
        return obj.nome

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'

class ContratoSerializer(serializers.ModelSerializer):
    imovel = ImovelSimplificadoSerializer(read_only=True)
    pagamentos = PagamentoSerializer(many=True, read_only=True)
    
    inquilino = ClienteSimplificadoSerializer(read_only=True)
    proprietario = ClienteSimplificadoSerializer(read_only=True)

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
            'pagamentos', 'inquilino_id', 'proprietario_id', 'conteudo_personalizado'
        ]
        read_only_fields = ('data_cadastro',)

class ContratoCriacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = '__all__'
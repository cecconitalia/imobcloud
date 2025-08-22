# C:\wamp64\www\ImobCloud\app_contratos\serializers.py
from rest_framework import serializers
from .models import Contrato, Pagamento
from app_imoveis.serializers import ImovelSerializer
from app_clientes.serializers import ClienteSerializer as ClienteDetailSerializer
from app_clientes.models import Cliente
from app_imoveis.models import Imovel
from app_financeiro.models import FormaPagamento

class PagamentoSerializer(serializers.ModelSerializer):
    forma_pagamento_display = serializers.CharField(source='get_forma_pagamento_recebida_display', read_only=True)
    class Meta:
        model = Pagamento
        fields = '__all__'

class ClienteSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome_completo']

class ImovelSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imovel
        fields = ['id', 'titulo_anuncio', 'endereco', 'codigo_referencia']

class ContratoListSerializer(serializers.ModelSerializer):
    imovel = ImovelSimplificadoSerializer(read_only=True)
    inquilino = ClienteSimplificadoSerializer(read_only=True)
    proprietario = ClienteSimplificadoSerializer(read_only=True)
    
    class Meta:
        model = Contrato
        fields = ['id', 'imovel', 'inquilino', 'proprietario', 'tipo_contrato', 'data_inicio', 'status_contrato']


class ContratoDetailSerializer(serializers.ModelSerializer):
    imovel = ImovelSimplificadoSerializer(read_only=True)
    inquilino = ClienteSimplificadoSerializer(read_only=True)
    proprietario = ClienteSimplificadoSerializer(read_only=True)
    pagamentos = PagamentoSerializer(many=True, read_only=True)
    formas_pagamento = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Contrato
        fields = '__all__'


class ContratoWriteSerializer(serializers.ModelSerializer):
    imovel = serializers.PrimaryKeyRelatedField(queryset=Imovel.objects.all())
    inquilino = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all(), required=False)
    proprietario = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all(), required=False)
    formas_pagamento = serializers.PrimaryKeyRelatedField(
        queryset=FormaPagamento.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = Contrato
        # ==========================================================================================
        # <<< LISTA DE CAMPOS CORRIGIDA >>>
        fields = [
            'id', 'imovel', 'inquilino', 'proprietario', 'tipo_contrato',
            'data_inicio', 'data_fim', 'data_assinatura', 'duracao_meses',
            'valor_total', 'status_contrato', 'informacoes_adicionais',
            'formas_pagamento'
        ]
        # ==========================================================================================
        read_only_fields = ['imobiliaria']
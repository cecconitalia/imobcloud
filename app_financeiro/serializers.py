# app_financeiro/serializers.py

from rest_framework import serializers
from .models import Categoria, ContaBancaria, Transacao, FormaPagamento
from core.models import Imobiliaria

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        exclude = ['imobiliaria']

class ContaBancariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaBancaria
        exclude = ['imobiliaria']

class FormaPagamentoSerializer(serializers.ModelSerializer):
    imobiliaria = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = FormaPagamento
        fields = ['id', 'nome', 'slug', 'imobiliaria', 'ativo']
        
    def create(self, validated_data):
        user = self.context['request'].user
        imobiliaria = user.perfil.imobiliaria
        validated_data['imobiliaria'] = imobiliaria
        return super().create(validated_data)

class TransacaoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.StringRelatedField(source='categoria.nome', read_only=True)
    conta_bancaria_nome = serializers.StringRelatedField(source='conta_bancaria.nome', read_only=True)
    forma_pagamento_nome = serializers.StringRelatedField(source='forma_pagamento.nome', read_only=True)
    
    # ==========================================================================================
    # <<< NOVO CAMPO ADICIONADO PARA OBTER O NOME DO CLIENTE >>>
    cliente_nome = serializers.SerializerMethodField()
    # ==========================================================================================

    class Meta:
        model = Transacao
        fields = [
            'id', 
            'descricao', 
            'valor', 
            'tipo',
            'data_vencimento', 
            'data_pagamento', 
            'status', 
            'categoria', 
            'conta_bancaria', 
            'imovel',
            'contrato',
            'forma_pagamento',
            'categoria_nome',
            'conta_bancaria_nome',
            'forma_pagamento_nome',
            'cliente_nome' # <<< NOME DO CAMPO ADICIONADO À LISTA
        ]
        extra_kwargs = {
            'categoria': {'required': False, 'allow_null': True},
            'imovel': {'required': False, 'allow_null': True},
            'contrato': {'required': False, 'allow_null': True},
            'data_pagamento': {'required': False, 'allow_null': True},
            'forma_pagamento': {'required': False, 'allow_null': True},
        }

    # ==========================================================================================
    # <<< NOVA FUNÇÃO PARA PROCESSAR O CAMPO cliente_nome >>>
    def get_cliente_nome(self, obj):
        """
        Retorna o nome do inquilino se a transação estiver ligada a um contrato.
        """
        if obj.contrato and obj.contrato.inquilino:
            return obj.contrato.inquilino.nome_completo
        return "Avulso" # Retorna "Avulso" se não houver contrato/cliente vinculado
    # ==========================================================================================
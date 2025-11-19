# C:\wamp64\www\ImobCloud\app_financeiro\serializers.py

from rest_framework import serializers
from django.db.models import Sum
from .models import Categoria, Conta, Transacao, FormaPagamento

# --- Serializers Básicos (Modelos de Configuração) ---

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'tipo', 'imobiliaria']
        read_only_fields = ['imobiliaria']

class ContaSerializer(serializers.ModelSerializer):
    # Campo calculado dinamicamente
    saldo_atual = serializers.SerializerMethodField()

    class Meta:
        model = Conta
        # Adicionamos 'saldo_atual' aos campos retornados
        fields = ['id', 'nome', 'saldo_inicial', 'saldo_atual', 'imobiliaria']
        read_only_fields = ['imobiliaria', 'saldo_atual']

    def get_saldo_atual(self, obj):
        """
        Calcula o saldo atual somando receitas pagas e subtraindo despesas pagas
        do saldo inicial.
        """
        # Soma todas as RECEITAS com status PAGO vinculadas a esta conta
        total_receitas = obj.transacao_set.filter(
            status='PAGO', 
            tipo='RECEITA'
        ).aggregate(total=Sum('valor'))['total'] or 0

        # Soma todas as DESPESAS com status PAGO vinculadas a esta conta
        total_despesas = obj.transacao_set.filter(
            status='PAGO', 
            tipo='DESPESA'
        ).aggregate(total=Sum('valor'))['total'] or 0

        # Retorna o cálculo final
        return obj.saldo_inicial + total_receitas - total_despesas

class FormaPagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPagamento
        fields = ['id', 'nome', 'imobiliaria']
        read_only_fields = ['imobiliaria']

# --- Serializer de Transação de Listagem ---

class TransacaoListSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.SerializerMethodField()
    conta_nome = serializers.SerializerMethodField()
    forma_pagamento_nome = serializers.SerializerMethodField()
    cliente_nome = serializers.SerializerMethodField()
    
    # [NOVO CAMPO] Para exibir o ID da transação de origem (se for um repasse)
    transacao_origem = serializers.PrimaryKeyRelatedField(read_only=True) 

    class Meta:
        model = Transacao
        fields = [
            'id', 'descricao', 'valor', 'data_transacao', 'data_vencimento', 'data_pagamento',
            'tipo', 'status', 'observacoes',
            'categoria_nome', 'conta_nome', 'forma_pagamento_nome',
            'cliente_nome',
            'cliente', 'imovel', 'contrato',
            'transacao_origem' # CAMPO NOVO
        ]
        
    def get_categoria_nome(self, obj: Transacao):
        """ Retorna o nome da Categoria ou uma string vazia se for nulo. """
        return obj.categoria.nome if obj.categoria else ''

    def get_conta_nome(self, obj: Transacao):
        """ Retorna o nome da Conta ou uma string vazia se for nulo. """
        return obj.conta.nome if obj.conta else ''

    def get_forma_pagamento_nome(self, obj: Transacao):
        """ Retorna o nome da Forma de Pagamento ou uma string vazia se for nulo. """
        return obj.forma_pagamento.nome if obj.forma_pagamento else ''

    def get_cliente_nome(self, obj: Transacao):
        """ Retorna o valor da propriedade cliente_nome do modelo. """
        return obj.cliente_nome 


# --- Serializer Completo de Transação (Para criação/edição e detalhes) ---

class TransacaoSerializer(serializers.ModelSerializer):
    cliente_detalhes = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Transacao
        fields = '__all__' 
        read_only_fields = ['imobiliaria']

    def get_cliente_detalhes(self, obj):
        # Importa o ClienteSerializer internamente para evitar possíveis referências circulares
        try:
            from app_clientes.serializers import ClienteSerializer 
        except ImportError:
            return None

        cliente_obj = obj.cliente
        # Tenta pegar o inquilino se não houver cliente direto e houver contrato
        if not cliente_obj and obj.contrato and hasattr(obj.contrato, 'inquilino'):
            cliente_obj = obj.contrato.inquilino
            
        if cliente_obj:
            return ClienteSerializer(cliente_obj).data
        return None
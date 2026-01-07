# C:\wamp64\www\ImobCloud\app_financeiro\serializers.py

from rest_framework import serializers
from django.db.models import Sum
from .models import Categoria, Conta, Transacao, FormaPagamento
from app_clientes.models import Cliente
from app_imoveis.models import Imovel

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

# --- Serializer Principal de Transação (Criação/Edição) ---
# [IMPORTANTE] Este serializer é blindado contra erros de validação (400)

class TransacaoSerializer(serializers.ModelSerializer):
    # Campos Read-Only (O Frontend NÃO manda, o Backend define pelo Token)
    imobiliaria = serializers.PrimaryKeyRelatedField(read_only=True)
    
    # Campos Opcionais (Permitir Null explicitamente evita erro 400)
    cliente = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), required=False, allow_null=True
    )
    imovel = serializers.PrimaryKeyRelatedField(
        queryset=Imovel.objects.all(), required=False, allow_null=True
    )
    forma_pagamento = serializers.PrimaryKeyRelatedField(
        queryset=FormaPagamento.objects.all(), required=False, allow_null=True
    )
    
    # Validação de Data de Pagamento
    data_pagamento = serializers.DateField(required=False, allow_null=True)
    
    cliente_detalhes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Transacao
        fields = '__all__'
        read_only_fields = ['imobiliaria']

    def validate(self, data):
        """
        Validações extras de regra de negócio
        """
        # Se estiver PAGO, data_pagamento é obrigatória
        # Verifica se 'status' está no payload ou usa o da instância (edição)
        status = data.get('status')
        if not status and self.instance:
            status = self.instance.status
            
        data_pagamento = data.get('data_pagamento')
        if not data_pagamento and self.instance:
            data_pagamento = self.instance.data_pagamento

        if status == 'PAGO' and not data_pagamento:
             raise serializers.ValidationError({"data_pagamento": "A Data de Pagamento é obrigatória para status PAGO."})
        
        return data

    def get_cliente_detalhes(self, obj):
        try:
            from app_clientes.serializers import ClienteSerializer 
            cliente_obj = obj.cliente
            if not cliente_obj and obj.contrato and hasattr(obj.contrato, 'inquilino'):
                cliente_obj = obj.contrato.inquilino
            
            if cliente_obj:
                return ClienteSerializer(cliente_obj).data
        except ImportError:
            pass
        return None

# --- Serializer de Transação de Listagem (Leitura Otimizada) ---

class TransacaoListSerializer(serializers.ModelSerializer):
    """
    Serializer otimizado para LEITURA (Listagem). 
    Traz os nomes legíveis em vez de apenas IDs.
    """
    # Usando 'source' para pegar os nomes diretamente das relações
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True, default='')
    conta_nome = serializers.CharField(source='conta.nome', read_only=True, default='')
    forma_pagamento_nome = serializers.CharField(source='forma_pagamento.nome', read_only=True, default='')
    
    # Propriedade personalizada do model ou relação direta
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True, default='')
    imovel_titulo = serializers.CharField(source='imovel.titulo_anuncio', read_only=True, default='')
    
    transacao_origem = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Transacao
        fields = [
            'id', 'descricao', 'valor', 'data_transacao', 'data_vencimento', 'data_pagamento',
            'tipo', 'status', 'observacoes',
            'categoria', 'categoria_nome', 
            'conta', 'conta_nome', 
            'forma_pagamento', 'forma_pagamento_nome',
            'cliente', 'cliente_nome',
            'imovel', 'imovel_titulo', 
            'contrato',
            'transacao_origem'
        ]
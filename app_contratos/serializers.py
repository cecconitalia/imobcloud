# C:\wamp64\www\imobcloud\app_contratos\serializers.py

from rest_framework import serializers
from .models import Contrato, Pagamento
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from django.db import transaction
from app_financeiro.models import FormaPagamento 
from decimal import Decimal

# ====================================================================
# SERIALIZERS AUXILIARES
# ====================================================================

class ImovelSimplificadoSerializer(serializers.ModelSerializer):
    """ Serializer auxiliar para Imóveis (usado em listas e detalhes) """
    endereco_completo = serializers.SerializerMethodField()
    class Meta:
        model = Imovel
        fields = ['id', 'titulo_anuncio', 'logradouro', 'endereco_completo']

    def get_endereco_completo(self, obj):
        partes = [ obj.logradouro, obj.numero, obj.complemento, obj.bairro, obj.cidade, obj.estado ]
        endereco = ', '.join(filter(None, partes))
        return endereco or "Endereço não disponível"

class ClienteSimplificadoSerializer(serializers.ModelSerializer):
    """ Serializer auxiliar para Clientes (usado em listas e detalhes) """
    nome_display = serializers.SerializerMethodField()
    class Meta:
        model = Cliente
        fields = ['id', 'nome_display', 'documento']

    def get_nome_display(self, obj):
        if hasattr(obj, 'tipo_pessoa') and obj.tipo_pessoa == 'JURIDICA' and obj.razao_social:
            return obj.razao_social
        return obj.nome

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'

# ====================================================================
# SERIALIZER DE LEITURA E DETALHE (ContratoSerializer) - (CORRIGIDO)
# ====================================================================

class ContratoSerializer(serializers.ModelSerializer):
    """ Serializer para LEITURA (Detalhe/Visualização) """
    imovel_detalhes = ImovelSimplificadoSerializer(source='imovel', read_only=True)
    inquilino_detalhes = ClienteSimplificadoSerializer(source='inquilino', read_only=True)
    proprietario_detalhes = ClienteSimplificadoSerializer(source='proprietario', read_only=True)
    fiadores_detalhes = ClienteSimplificadoSerializer(source='fiadores', read_only=True, many=True)
    pagamentos = PagamentoSerializer(many=True, read_only=True)
    parte_principal_label = serializers.SerializerMethodField()
    valor_display = serializers.SerializerMethodField()
    financeiro_gerado = serializers.BooleanField(read_only=True)
    formas_pagamento = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Contrato
        fields = [
            'id', 'imobiliaria', 'tipo_contrato', 
            'valor_total', 'aluguel', 'taxa_administracao_percentual',
            'comissao_venda_percentual',
            'valor_comissao_acordado',
            'data_primeiro_vencimento',
            'data_vencimento_venda',
            'informacoes_adicionais', 'duracao_meses', 'status_contrato',
            'data_inicio', 'data_fim', 'data_assinatura', 'data_cadastro',
            'conteudo_personalizado',
            
            # IDs (necessários para o formulário de edição)
            'imovel',
            'inquilino',
            'proprietario', # <-- ESTA É A CORREÇÃO (garante que o ID seja enviado)

            # Detalhes (usados para exibição)
            'imovel_detalhes', 
            'inquilino_detalhes', 
            'proprietario_detalhes',
            'fiadores_detalhes', 
            
            # Campos relacionados
            'pagamentos',
            'parte_principal_label',
            'valor_display',
            'formas_pagamento',
            'fiadores', 
            'financeiro_gerado',
        ]
        read_only_fields = ('data_cadastro', 'imobiliaria')

    def get_parte_principal_label(self, obj):
        return "Comprador" if obj.tipo_contrato == Contrato.TipoContrato.VENDA else "Inquilino"

    def get_valor_display(self, obj):
        try:
            if obj.tipo_contrato == Contrato.TipoContrato.VENDA and obj.valor_total is not None:
                valor_formatado = f"R$ {obj.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return valor_formatado
            if obj.tipo_contrato == Contrato.TipoContrato.ALUGUEL and obj.aluguel is not None:
                valor_formatado = f"R$ {obj.aluguel:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return f"{valor_formatado} /mês"
        except Exception: pass 
        return "R$ -"

# ====================================================================
# SERIALIZER DE CRIAÇÃO E ATUALIZAÇÃO (ContratoCriacaoSerializer)
# ====================================================================

class ContratoCriacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para CRIAÇÃO/ATUALIZAÇÃO. Aceita proprietário vindo do frontend.
    """
    
    imovel = serializers.PrimaryKeyRelatedField(
        queryset=Imovel.objects.all(),
        required=True
    )
    inquilino = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        required=True
    )
    # Proprietario é obrigatório e vem do frontend
    proprietario = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        required=True
    )
    
    fiadores = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        required=False,
        many=True 
    )

    formas_pagamento = serializers.PrimaryKeyRelatedField(
        queryset=FormaPagamento.objects.all(),
        required=False,
        many=True
    )

    valor_total = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    aluguel = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    duracao_meses = serializers.IntegerField(required=False, allow_null=True, default=12)
    
    class Meta:
        model = Contrato
        
        # Proprietario está incluído nos fields
        fields = [
            'tipo_contrato',
            'imovel',
            'inquilino',
            'proprietario',
            'fiadores', 
            'aluguel',
            'valor_total',
            'taxa_administracao_percentual', 
            'comissao_venda_percentual',
            'valor_comissao_acordado',
            'data_primeiro_vencimento',
            'data_vencimento_venda',
            'informacoes_adicionais',
            'duracao_meses',
            'status_contrato',
            'data_inicio',
            'data_fim',
            'data_assinatura',
            'conteudo_personalizado',
            'formas_pagamento', 
        ]
        read_only_fields = ('imobiliaria', 'data_cadastro')
        
    def validate(self, data):
        imovel = data.get('imovel')
        proprietario = data.get('proprietario')
        inquilino = data.get('inquilino')
        
        # --- VALIDAÇÃO CRÍTICA: Imóvel pertence ao Proprietário? ---
        if imovel and proprietario:
            if imovel.proprietario != proprietario:
                raise serializers.ValidationError({"imovel": "Este imóvel não pertence ao proprietário selecionado. Por favor, recarregue a lista de imóveis."})
        elif not proprietario:
             raise serializers.ValidationError({"proprietario": "O proprietário é obrigatório."})
        # -------------------------------------------------------------------------

        # 1. Validação Inquilino/Proprietário
        if inquilino == proprietario:
            raise serializers.ValidationError("O inquilino/comprador e o proprietário não podem ser a mesma pessoa.")

        # 2. Validação Fiador
        fiadores_list = data.get('fiadores', [])
        for fiador in fiadores_list:
            if fiador == inquilino:
                 raise serializers.ValidationError({"fiadores": "O fiador não pode ser o mesmo que o inquilino."})
            if fiador == proprietario:
                 raise serializers.ValidationError({"fiadores": "O fiador não pode ser o mesmo que o proprietário."})

        # ... (Restante da validação de tipo e valores)
        
        tipo = data.get('tipo_contrato')
        valor_aluguel = data.get('aluguel')
        valor_venda = data.get('valor_total')
        data_primeiro_vencimento = data.get('data_primeiro_vencimento')
        data_vencimento_venda = data.get('data_vencimento_venda')
        
        tipo_limpo = None
        
        if tipo:
             tipo_limpo = tipo.strip().upper().replace('"', '').replace("'", "")
             if tipo_limpo not in [Contrato.TipoContrato.ALUGUEL, Contrato.TipoContrato.VENDA]:
                 raise serializers.ValidationError({"tipo_contrato": f"O tipo de contrato '{tipo}' é inválido."})
             data['tipo_contrato'] = tipo_limpo 
        
        if tipo_limpo == Contrato.TipoContrato.ALUGUEL:
            if not valor_aluguel:
                raise serializers.ValidationError({"aluguel": "Este campo é obrigatório para contratos de Aluguel."})
            if not data_primeiro_vencimento:
                raise serializers.ValidationError({"data_primeiro_vencimento": "A data do primeiro vencimento é obrigatória para Aluguel."})

            data['valor_total'] = None 
            data['data_vencimento_venda'] = None

        elif tipo_limpo == Contrato.TipoContrato.VENDA:
            if not valor_venda:
                raise serializers.ValidationError({"valor_total": "Este campo é obrigatório para contratos de Venda."})
            if not data_vencimento_venda:
                raise serializers.ValidationError({"data_vencimento_venda": "A data de vencimento/quitação é obrigatória para Venda."})

            data['aluguel'] = None 
            data['duracao_meses'] = None 
            data['data_primeiro_vencimento'] = None
            
        status_contrato = data.get('status_contrato')
        
        if status_contrato == Contrato.Status.ATIVO and imovel:
            instance_pk = self.instance.pk if self.instance else None
            
            query_conflitos = Contrato.objects.filter(
                imovel=imovel,
                status_contrato=Contrato.Status.ATIVO,
                tipo_contrato=tipo_limpo
            ).exclude(pk=instance_pk)
            
            if query_conflitos.exists():
                raise serializers.ValidationError({
                    "status_contrato": f"Este imóvel já possui outro contrato de {tipo_limpo.capitalize()} ATIVO."
                })

        return data

# ====================================================================
# SERIALIZER DE LISTAGEM (ContratoListSerializer) - (Corrigido anteriormente)
# ====================================================================

class ContratoListSerializer(serializers.ModelSerializer):
    """
    Serializer leve para a listagem de Contratos.
    Modificado para enviar os dados aninhados que o ContratosView.vue espera.
    """
    
    # CORREÇÃO: Usar os serializers simplificados para corresponder ao frontend
    imovel_detalhes = ImovelSimplificadoSerializer(source='imovel', read_only=True)
    inquilino_detalhes = ClienteSimplificadoSerializer(source='inquilino', read_only=True)
    proprietario_detalhes = ClienteSimplificadoSerializer(source='proprietario', read_only=True)
    
    # CORREÇÃO: Adicionar os campos que o frontend (ContratosView.vue) está renderizando
    parte_principal_label = serializers.SerializerMethodField()
    valor_display = serializers.SerializerMethodField()

    financeiro_gerado = serializers.BooleanField(read_only=True)

    class Meta:
        model = Contrato
        fields = [
            'id', 'tipo_contrato', 'status_contrato',
            
            # Campos aninhados que o frontend espera
            'imovel_detalhes', 
            'inquilino_detalhes',
            'proprietario_detalhes',
            
            # Campos de exibição que o frontend espera
            'parte_principal_label',
            'valor_display',

            # Campos de dados simples
            'aluguel', 'valor_total', # Mantidos para referência, embora valor_display seja usado
            'data_inicio', 'data_fim', 'data_assinatura',
            'financeiro_gerado',

            # Campos de ID (para filtros, se necessário, mas não essenciais para exibição)
            'imovel', 
            'inquilino',
            'proprietario', 
        ]
        
    # --- MÉTODOS ADICIONADOS (necessários para os SerializerMethodField) ---

    def get_parte_principal_label(self, obj):
        # Lógica copiada do ContratoSerializer (detalhado)
        return "Comprador" if obj.tipo_contrato == Contrato.TipoContrato.VENDA else "Inquilino"

    def get_valor_display(self, obj):
        # Lógica copiada do ContratoSerializer (detalhado)
        try:
            if obj.tipo_contrato == Contrato.TipoContrato.VENDA and obj.valor_total is not None:
                valor_formatado = f"R$ {obj.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return valor_formatado
            if obj.tipo_contrato == Contrato.TipoContrato.ALUGUEL and obj.aluguel is not None:
                valor_formatado = f"R$ {obj.aluguel:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return f"{valor_formatado} /mês"
        except Exception: pass 
        return "R$ -"
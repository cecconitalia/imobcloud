# C:\wamp64\www\imobcloud\app_contratos\serializers.py

from rest_framework import serializers
from .models import Contrato, Pagamento, ModeloContrato 
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from django.db import transaction
from app_financeiro.models import FormaPagamento 
from decimal import Decimal

# (Serializers Auxiliares e ModeloContratoSerializer permanecem inalterados)
class ImovelSimplificadoSerializer(serializers.ModelSerializer):
    endereco_completo = serializers.SerializerMethodField()
    class Meta:
        model = Imovel
        fields = ['id', 'titulo_anuncio', 'logradouro', 'endereco_completo']
    def get_endereco_completo(self, obj):
        partes = [ obj.logradouro, obj.numero, obj.complemento, obj.bairro, obj.cidade, obj.estado ]
        endereco = ', '.join(filter(None, partes))
        return endereco or "Endereço não disponível"

class ClienteSimplificadoSerializer(serializers.ModelSerializer):
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

class ModeloContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeloContrato
        fields = [
            'id', 'nome', 'tipo_contrato', 'conteudo', 
            'padrao', 'data_cadastro', 'data_atualizacao'
        ]
        read_only_fields = ('imobiliaria', 'data_cadastro', 'data_atualizacao')
    def validate(self, data):
        if data.get('padrao', False):
            imobiliaria = self.context['request'].user.perfil.imobiliaria
            tipo_contrato = data.get('tipo_contrato')
            query = ModeloContrato.objects.filter(
                imobiliaria=imobiliaria,
                tipo_contrato=tipo_contrato,
                padrao=True
            )
            if self.instance:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise serializers.ValidationError({
                    "padrao": f"Já existe um modelo padrão para {tipo_contrato}. Desmarque o outro modelo antes de salvar este como padrão."
                })
        return data

# (ContratoSerializer de LEITURA permanece inalterado)
class ContratoSerializer(serializers.ModelSerializer):
    imovel_detalhes = ImovelSimplificadoSerializer(source='imovel', read_only=True)
    inquilino_detalhes = ClienteSimplificadoSerializer(source='inquilino', read_only=True)
    proprietario_detalhes = ClienteSimplificadoSerializer(source='proprietario', read_only=True)
    fiadores_detalhes = ClienteSimplificadoSerializer(source='fiadores', read_only=True, many=True)
    modelo_utilizado = ModeloContratoSerializer(read_only=True)
    pagamentos = PagamentoSerializer(many=True, read_only=True)
    parte_principal_label = serializers.SerializerMethodField()
    valor_display = serializers.SerializerMethodField()
    financeiro_gerado = serializers.BooleanField(read_only=True)
    formas_pagamento = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Contrato
        fields = [
            'id', 'imobiliaria', 'tipo_contrato', 
            'modelo_utilizado', 
            'valor_total', 'aluguel', 'taxa_administracao_percentual',
            'comissao_venda_percentual',
            'valor_comissao_acordado',
            'data_primeiro_vencimento',
            'data_vencimento_venda',
            'informacoes_adicionais', 'duracao_meses', 'status_contrato',
            'data_inicio', 'data_fim', 'data_assinatura', 'data_cadastro',
            'conteudo_personalizado',
            'imovel',
            'inquilino',
            'proprietario', 
            'imovel_detalhes', 
            'inquilino_detalhes', 
            'proprietario_detalhes',
            'fiadores_detalhes', 
            'pagamentos',
            'parte_principal_label',
            'valor_display',
            'formas_pagamento',
            'fiadores', 
            'financeiro_gerado',
            'excluido', 
        ]
        read_only_fields = ('data_cadastro', 'imobiliaria', 'excluido', 'conteudo_personalizado')
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
# SERIALIZER DE CRIAÇÃO E ATUALIZAÇÃO (ContratoCriacaoSerializer) - (CORRIGIDO)
# ====================================================================

class ContratoCriacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para CRIAÇÃO/ATUALIZAÇÃO. Aceita proprietário vindo do frontend.
    """
    
    modelo_utilizado = serializers.PrimaryKeyRelatedField(
        queryset=ModeloContrato.objects.all(),
        required=False, 
        allow_null=True
    )
    imovel = serializers.PrimaryKeyRelatedField(
        queryset=Imovel.objects.all(),
        required=True
    )
    inquilino = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        required=True
    )
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
        
        fields = [
            'tipo_contrato',
            'modelo_utilizado', 
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
            'formas_pagamento', 
        ]
        
        read_only_fields = ('imobiliaria', 'data_cadastro', 'excluido')
        
    def validate_modelo_utilizado(self, value):
        imobiliaria_usuario = self.context['request'].user.perfil.imobiliaria
        if value and value.imobiliaria != imobiliaria_usuario:
            raise serializers.ValidationError("Este modelo de contrato não pertence à sua imobiliária.")
        return value

    # ==========================================================
    # === CORREÇÃO: Método validate() ATUALIZADO             ===
    # ==========================================================
    def validate(self, data):
        """
        Validação que agora suporta partial updates (ex: ação 'ativar')
        buscando dados do self.instance quando não estão em 'data'.
        """
        instance = self.instance 

        # 1. Coleta os dados (novos ou existentes)
        # Se 'instance' existe (é um update), usa o valor do instance como fallback.
        # Se não (é um create), o .get() retornará None se a chave não estiver em 'data'.
        imovel = data.get('imovel', instance.imovel if instance else None)
        proprietario = data.get('proprietario', instance.proprietario if instance else None)
        inquilino = data.get('inquilino', instance.inquilino if instance else None)
        tipo_contrato = data.get('tipo_contrato', instance.tipo_contrato if instance else None)
        aluguel = data.get('aluguel', instance.aluguel if instance else None)
        valor_total = data.get('valor_total', instance.valor_total if instance else None)
        data_primeiro_vencimento = data.get('data_primeiro_vencimento', instance.data_primeiro_vencimento if instance else None)
        data_vencimento_venda = data.get('data_vencimento_venda', instance.data_vencimento_venda if instance else None)
        status_contrato = data.get('status_contrato', instance.status_contrato if instance else None)
        
        # Fiadores: se 'fiadores' foi passado, usa a lista de 'data'. 
        # Se não, usa a lista existente do 'instance'.
        fiadores_list = data.get('fiadores', instance.fiadores.all() if instance else [])
        
        # 2. Executa as validações com os dados consolidados
        if imovel and proprietario:
            if imovel.proprietario != proprietario:
                raise serializers.ValidationError({"imovel": "Este imóvel não pertence ao proprietário selecionado. Por favor, recarregue a lista de imóveis."})
        elif not proprietario:
             raise serializers.ValidationError({"proprietario": "O proprietário é obrigatório."})

        if inquilino == proprietario:
            raise serializers.ValidationError("O inquilino/comprador e o proprietário não podem ser a mesma pessoa.")
        
        # Só valida os fiadores se o campo 'fiadores' foi enviado na requisição (create ou update)
        if 'fiadores' in data: 
            for fiador in fiadores_list:
                if fiador == inquilino:
                     raise serializers.ValidationError({"fiadores": "O fiador não pode ser o mesmo que o inquilino."})
                if fiador == proprietario:
                     raise serializers.ValidationError({"fiadores": "O fiador não pode ser o mesmo que o proprietário."})

        # 3. Validação de Tipo/Valores
        tipo_limpo = None
        if tipo_contrato:
             tipo_limpo = str(tipo_contrato).strip().upper().replace('"', '').replace("'", "")
             if tipo_limpo not in [Contrato.TipoContrato.ALUGUEL, Contrato.TipoContrato.VENDA]:
                 raise serializers.ValidationError({"tipo_contrato": f"O tipo de contrato '{tipo_contrato}' é inválido."})
             data['tipo_contrato'] = tipo_limpo # Garante que o valor salvo está limpo
        
        if tipo_limpo == Contrato.TipoContrato.ALUGUEL:
            if not aluguel:
                raise serializers.ValidationError({"aluguel": "Este campo é obrigatório para contratos de Aluguel."})
            if not data_primeiro_vencimento:
                raise serializers.ValidationError({"data_primeiro_vencimento": "A data do primeiro vencimento é obrigatória para Aluguel."})
            data['valor_total'] = None 
            data['data_vencimento_venda'] = None

        elif tipo_limpo == Contrato.TipoContrato.VENDA:
            if not valor_total:
                raise serializers.ValidationError({"valor_total": "Este campo é obrigatório para contratos de Venda."})
            if not data_vencimento_venda:
                raise serializers.ValidationError({"data_vencimento_venda": "A data de vencimento/quitação é obrigatória para Venda."})
            data['aluguel'] = None 
            data['duracao_meses'] = None 
            data['data_primeiro_vencimento'] = None
            
        # 4. Validação de Conflito de Status
        if status_contrato == Contrato.Status.ATIVO and imovel:
            instance_pk = self.instance.pk if self.instance else None
            
            query_conflitos = Contrato.objects.filter(
                imovel=imovel,
                status_contrato=Contrato.Status.ATIVO,
                tipo_contrato=tipo_limpo,
                excluido=False 
            ).exclude(pk=instance_pk)
            
            if query_conflitos.exists():
                raise serializers.ValidationError({
                    "status_contrato": f"Este imóvel já possui outro contrato de {tipo_limpo.capitalize()} ATIVO."
                })

        return data
    # ==========================================================

    def _executar_logica_financeira(self, contrato):
        if contrato.status_contrato == Contrato.Status.ATIVO:
            if contrato.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
                contrato.gerar_financeiro_aluguel()
            elif contrato.tipo_contrato == Contrato.TipoContrato.VENDA:
                contrato.criar_transacao_comissao()

    @transaction.atomic
    def create(self, validated_data):
        contrato = super().create(validated_data)
        self._executar_logica_financeira(contrato)
        return contrato

    @transaction.atomic
    def update(self, instance, validated_data):
        status_anterior = instance.status_contrato
        
        if 'modelo_utilizado' in validated_data:
            novo_modelo = validated_data.get('modelo_utilizado')
            modelo_antigo = instance.modelo_utilizado
            
            if novo_modelo != modelo_antigo:
                instance.conteudo_personalizado = None
                
        contrato = super().update(instance, validated_data)
        
        # Lógica de geração financeira (permanece a mesma)
        if status_anterior != Contrato.Status.ATIVO and contrato.status_contrato == Contrato.Status.ATIVO:
            self._executar_logica_financeira(contrato)
            
        return contrato

# (ContratoListSerializer inalterado)
class ContratoListSerializer(serializers.ModelSerializer):
    imovel_detalhes = ImovelSimplificadoSerializer(source='imovel', read_only=True)
    inquilino_detalhes = ClienteSimplificadoSerializer(source='inquilino', read_only=True)
    proprietario_detalhes = ClienteSimplificadoSerializer(source='proprietario', read_only=True)
    parte_principal_label = serializers.SerializerMethodField()
    valor_display = serializers.SerializerMethodField()
    financeiro_gerado = serializers.BooleanField(read_only=True)
    class Meta:
        model = Contrato
        fields = [
            'id', 'tipo_contrato', 'status_contrato',
            'imovel_detalhes', 
            'inquilino_detalhes',
            'proprietario_detalhes',
            'parte_principal_label',
            'valor_display',
            'aluguel', 'valor_total', 
            'data_inicio', 'data_fim', 'data_assinatura',
            'financeiro_gerado',
            'imovel', 
            'inquilino',
            'proprietario', 
        ]
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
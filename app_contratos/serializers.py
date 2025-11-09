# C:\wamp64\www\imobcloud\app_contratos\serializers.py

from rest_framework import serializers
from .models import Contrato, Pagamento
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from django.db import transaction
from app_financeiro.models import FormaPagamento 


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
        if obj.tipo_pessoa == 'JURIDICA' and obj.razao_social:
            return obj.razao_social
        return obj.nome

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'

class ContratoSerializer(serializers.ModelSerializer):
    # Serializer para LEITURA (Listagem)
    imovel_detalhes = ImovelSimplificadoSerializer(source='imovel', read_only=True)
    inquilino_detalhes = ClienteSimplificadoSerializer(source='inquilino', read_only=True)
    proprietario_detalhes = ClienteSimplificadoSerializer(source='proprietario', read_only=True)
    
    fiadores_detalhes = ClienteSimplificadoSerializer(source='fiadores', read_only=True, many=True)
    
    pagamentos = PagamentoSerializer(many=True, read_only=True)
    parte_principal_label = serializers.SerializerMethodField()
    valor_display = serializers.SerializerMethodField()

    formas_pagamento = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Contrato
        fields = [
            'id', 'imobiliaria', 'tipo_contrato', 
            'valor_total', 'aluguel', 
            'informacoes_adicionais', 'duracao_meses', 'status_contrato',
            'data_inicio', 'data_fim', 'data_assinatura', 'data_cadastro',
            'conteudo_personalizado',
            
            # Campos Read-only (para listagem)
            'imovel_detalhes', 
            'inquilino_detalhes', 
            'proprietario_detalhes',
            'fiadores_detalhes', 
            'pagamentos',
            'parte_principal_label',
            'valor_display',
            'formas_pagamento',
            
            # Campo de IDs de fiadores (para o v-model do form)
            'fiadores', 
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


class ContratoCriacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para CRIAÇÃO/ATUALIZAÇÃO.
    """
    
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
    
    # Campo M2M 1: Fiadores
    fiadores = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        required=False,
        many=True 
    )

    # Campo M2M 2: Formas de Pagamento
    formas_pagamento = serializers.PrimaryKeyRelatedField(
        queryset=FormaPagamento.objects.all(),
        required=False,
        many=True
    )

    # Campos de valor (para validação condicional)
    valor_total = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    aluguel = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    duracao_meses = serializers.IntegerField(required=False, allow_null=True, default=12)
    
    class Meta:
        model = Contrato
        
        # Lista explícita de campos para garantir que todos os M2M sejam processados.
        fields = [
            'tipo_contrato',
            'imovel',
            'inquilino',
            'proprietario',
            'fiadores', 
            'aluguel',
            'valor_total',
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
        # 1. Validação Inquilino/Proprietário
        if data.get('inquilino') == data.get('proprietario'):
            raise serializers.ValidationError("O inquilino/comprador e o proprietário não podem ser a mesma pessoa.")

        # 2. Validação Fiador
        fiadores_list = data.get('fiadores', [])
        inquilino = data.get('inquilino')
        proprietario = data.get('proprietario')

        for fiador in fiadores_list:
            if fiador == inquilino:
                 raise serializers.ValidationError({"fiadores": "O fiador não pode ser o mesmo que o inquilino."})
            if fiador == proprietario:
                 raise serializers.ValidationError({"fiadores": "O fiador não pode ser o mesmo que o proprietário."})

        tipo = data.get('tipo_contrato')
        valor_aluguel = data.get('aluguel')
        valor_venda = data.get('valor_total')
        
        tipo_limpo = None
        
        # 3. Sanitização e Validação do tipo_contrato
        if tipo:
             tipo_limpo = tipo.strip().upper().replace('"', '').replace("'", "")
             if tipo_limpo not in [Contrato.TipoContrato.ALUGUEL, Contrato.TipoContrato.VENDA]:
                 raise serializers.ValidationError({"tipo_contrato": f"O tipo de contrato '{tipo}' é inválido."})
             data['tipo_contrato'] = tipo_limpo 
        
        # 4. Validação Condicional de Valores
        if tipo_limpo == Contrato.TipoContrato.ALUGUEL:
            if not valor_aluguel:
                raise serializers.ValidationError({"aluguel": "Este campo é obrigatório para contratos de Aluguel."})
            data['valor_total'] = None 

        elif tipo_limpo == Contrato.TipoContrato.VENDA:
            if not valor_venda:
                raise serializers.ValidationError({"valor_total": "Este campo é obrigatório para contratos de Venda."})
            data['aluguel'] = None 
            data['duracao_meses'] = None 
            
        # ==================================================================
        # CORREÇÃO: Validação de Contrato Ativo Duplicado
        # Movida para cá (do models.py) para retornar um erro 400
        # formatado corretamente para o frontend.
        # ==================================================================
        status_contrato = data.get('status_contrato')
        imovel = data.get('imovel')
        
        if status_contrato == Contrato.Status.ATIVO and imovel:
            # Pega o 'self.instance' (o contrato atual) se for uma edição
            instance_pk = self.instance.pk if self.instance else None
            
            query_conflitos = Contrato.objects.filter(
                imovel=imovel,
                status_contrato=Contrato.Status.ATIVO,
                tipo_contrato=tipo_limpo
            ).exclude(pk=instance_pk)
            
            if query_conflitos.exists():
                # Esta é a mensagem de erro que será enviada ao frontend
                raise serializers.ValidationError({
                    "status_contrato": f"Este imóvel já possui outro contrato de {tipo_limpo.capitalize()} ATIVO."
                })

        return data
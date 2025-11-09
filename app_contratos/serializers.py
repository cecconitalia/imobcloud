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
    
    # CORREÇÃO: Alterado para 'fiadores' (plural) e 'many=True'
    fiadores_detalhes = ClienteSimplificadoSerializer(source='fiadores', read_only=True, many=True)
    
    pagamentos = PagamentoSerializer(many=True, read_only=True)
    parte_principal_label = serializers.SerializerMethodField()
    valor_display = serializers.SerializerMethodField()

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
            'fiadores_detalhes', # CORRIGIDO (plural)
            'pagamentos',
            'parte_principal_label',
            'valor_display',
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
    
    # ==================================================================
    # CORREÇÃO: Campos explícitos para garantir que o Imóvel (e outros FKs) 
    # sejam salvos. O seu frontend envia 'imovel', 'inquilino', 'proprietario'.
    # ==================================================================
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
    
    # ==================================================================
    # CORREÇÃO: Campo 'fiadores' (plural) com many=True (M2M)
    # (Isto já estava correto no seu ficheiro)
    # ==================================================================
    fiadores = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        required=False,
        many=True 
    )

    # Campos de valor (para validação condicional)
    valor_total = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    aluguel = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    duracao_meses = serializers.IntegerField(required=False, allow_null=True, default=12)
    
    class Meta:
        model = Contrato
        fields = '__all__'
        read_only_fields = ('imobiliaria', 'data_cadastro')
        
    def validate(self, data):
        # 1. Validação Inquilino/Proprietário
        if data.get('inquilino') == data.get('proprietario'):
            raise serializers.ValidationError("O inquilino/comprador e o proprietário não podem ser a mesma pessoa.")

        # Validação Fiador: Agora itera na lista
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
        
        # 2. Sanitização e Validação do tipo_contrato
        if tipo:
             tipo_limpo = tipo.strip().upper().replace('"', '').replace("'", "")
             if tipo_limpo not in [Contrato.TipoContrato.ALUGUEL, Contrato.TipoContrato.VENDA]:
                 raise serializers.ValidationError({"tipo_contrato": f"O tipo de contrato '{tipo}' é inválido."})
             data['tipo_contrato'] = tipo_limpo 
        
        # 3. Validação Condicional de Valores
        if tipo_limpo == Contrato.TipoContrato.ALUGUEL:
            if not valor_aluguel:
                raise serializers.ValidationError({"aluguel": "Este campo é obrigatório para contratos de Aluguel."})
            data['valor_total'] = None 

        elif tipo_limpo == Contrato.TipoContrato.VENDA:
            if not valor_venda:
                raise serializers.ValidationError({"valor_total": "Este campo é obrigatório para contratos de Venda."})
            data['aluguel'] = None 
            data['duracao_meses'] = None 
            
        return data
# C:\wamp64\www\imobcloud\app_contratos\serializers.py

from rest_framework import serializers
from .models import Contrato, Pagamento # Importa o modelo Contrato para usar o choices
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
    """ Serializer simplificado que exibe o nome correto do cliente e documento. """
    nome_display = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = ['id', 'nome_display', 'documento'] # Adicionado 'documento'

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
    # Serializer para LISTAGEM (como em ContratosView.vue)
    imovel_detalhes = ImovelSimplificadoSerializer(source='imovel', read_only=True)
    inquilino_detalhes = ClienteSimplificadoSerializer(source='inquilino', read_only=True)
    proprietario_detalhes = ClienteSimplificadoSerializer(source='proprietario', read_only=True)
    
    pagamentos = PagamentoSerializer(many=True, read_only=True)
    
    parte_principal_label = serializers.SerializerMethodField()
    valor_display = serializers.SerializerMethodField()

    # Campos de 'write_only' para criação/atualização (usados em ContratoFormView.vue)
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
    imovel_id = serializers.PrimaryKeyRelatedField(
        source='imovel',
        queryset=Imovel.objects.all(),
        write_only=True,
        required=True
    )

    class Meta:
        model = Contrato
        fields = [
            'id', 'imobiliaria', 'tipo_contrato', 
            'valor_total', 'aluguel', # 'aluguel' mantido aqui para o get_valor_display
            'informacoes_adicionais', 'duracao_meses', 'status_contrato',
            'data_inicio', 'data_fim', 'data_assinatura', 'data_cadastro',
            'conteudo_personalizado',
            
            # Campos Read-only (para listagem)
            'imovel_detalhes', 
            'inquilino_detalhes', 
            'proprietario_detalhes',
            'pagamentos',
            'parte_principal_label',
            'valor_display',

            # Campos Write-only (para formulário)
            'inquilino_id', 
            'proprietario_id',
            'imovel_id',
        ]
        read_only_fields = ('data_cadastro', 'imobiliaria')

    def get_parte_principal_label(self, obj):
        """ Retorna o rótulo correto para a "outra parte" do contrato. """
        # CORREÇÃO: Comparando com o valor UPPERCASE do TextChoice
        return "Comprador" if obj.tipo_contrato == Contrato.TipoContrato.VENDA else "Inquilino"

    def get_valor_display(self, obj):
        """ Retorna o valor formatado correto (mensal ou total). """
        try:
            # CORREÇÃO: Comparando com o valor UPPERCASE do TextChoice
            if obj.tipo_contrato == Contrato.TipoContrato.VENDA and obj.valor_total is not None:
                valor_formatado = f"R$ {obj.valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return valor_formatado
            # CORREÇÃO: Comparando com o valor UPPERCASE do TextChoice e usando o campo 'aluguel'
            if obj.tipo_contrato == Contrato.TipoContrato.ALUGUEL and obj.aluguel is not None:
                valor_formatado = f"R$ {obj.aluguel:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                return f"{valor_formatado} /mês"
        except Exception:
            pass 
        return "R$ -"


class ContratoCriacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para criação/atualização. Implementa validação customizada para os valores.
    """
    
    # Definimos os campos de valor explicitamente como NÃO obrigatórios na serialização
    # (A validação 'validate' abaixo os tornará obrigatórios condicionalmente)
    valor_total = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    aluguel = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)
    duracao_meses = serializers.IntegerField(required=False, allow_null=True, default=12)
    
    class Meta:
        model = Contrato
        fields = '__all__'
        # Campos preenchidos pelo código (na view) devem ser read-only
        read_only_fields = ('imobiliaria', 'status_contrato', 'data_cadastro')
        
    def validate(self, data):
        # 1. Validação Inquilino/Proprietário
        if data.get('inquilino') == data.get('proprietario'):
            raise serializers.ValidationError("O inquilino/comprador e o proprietário não podem ser a mesma pessoa.")

        tipo = data.get('tipo_contrato')
        valor_aluguel = data.get('aluguel')
        valor_venda = data.get('valor_total')
        
        tipo_limpo = None
        
        # 2. Sanitização e Validação do tipo_contrato
        if tipo:
             # Limpa aspas, espaços e força o UPPERCASE
             tipo_limpo = tipo.strip().upper().replace('"', '').replace("'", "")
             # Compara com os valores definidos nos TextChoices do modelo
             if tipo_limpo not in [Contrato.TipoContrato.ALUGUEL, Contrato.TipoContrato.VENDA]:
                 raise serializers.ValidationError({"tipo_contrato": f"O tipo de contrato '{tipo}' é inválido."})
             data['tipo_contrato'] = tipo_limpo # Salva o valor limpo (UPPERCASE)
        
        # 3. Validação Condicional de Valores
        
        # CORREÇÃO: Usando 'tipo_limpo' (UPPERCASE) na verificação
        if tipo_limpo == Contrato.TipoContrato.ALUGUEL:
            if not valor_aluguel:
                raise serializers.ValidationError({"aluguel": "Este campo é obrigatório para contratos de Aluguel."})
            data['valor_total'] = None # Zera o valor_total em aluguel

        # CORREÇÃO: Usando 'tipo_limpo' (UPPERCASE) na verificação
        elif tipo_limpo == Contrato.TipoContrato.VENDA:
            if not valor_venda:
                raise serializers.ValidationError({"valor_total": "Este campo é obrigatório para contratos de Venda."})
            data['aluguel'] = None # Zera o aluguel em venda
            data['duracao_meses'] = None # Venda não tem duração
            
        return data
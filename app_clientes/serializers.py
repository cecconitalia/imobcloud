# C:\wamp64\www\ImobCloud\app_clientes\serializers.py

from rest_framework import serializers
from .models import Cliente, Visita, Atividade, Oportunidade, Tarefa, FunilEtapa, apenas_numeros
from core.models import PerfilUsuario
from app_imoveis.models import Imovel
from django.contrib.auth import get_user_model

User = get_user_model()

# ===================================================================
# Serializers Auxiliares (para representação em outras partes do sistema)
# ===================================================================

class ResponsavelSimplificadoSerializer(serializers.ModelSerializer):
    """ Exibe apenas o essencial do responsável para listagens. """
    class Meta:
        model = User
        fields = ['id', 'first_name', 'username']

# ===================================================================
# Serializers Principais das Entidades
# ===================================================================

class VisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visita
        fields = '__all__'

# --- INÍCIO DA CORREÇÃO ---
class UsuarioSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'username']

class AtividadeSerializer(serializers.ModelSerializer):
    registrado_por_obj = UsuarioSimplesSerializer(source='registrado_por', read_only=True)

    class Meta:
        model = Atividade
        fields = [
            'id', 'tipo', 'descricao', 'data_criacao', 
            'registrado_por', 'registrado_por_obj', 'cliente'
        ]
        read_only_fields = ['registrado_por']
# --- FIM DA CORREÇÃO ---

class TarefaSerializer(serializers.ModelSerializer):
    """ Serializer para o modelo Tarefa. """
    class Meta:
        model = Tarefa
        fields = [
            'id', 'titulo', 'descricao', 'data_vencimento', 'concluida', 
            'oportunidade', 'responsavel', 'google_calendar_event_id',
            'observacoes_finalizacao'
        ]
        read_only_fields = ['responsavel']

# --- SERIALIZER DE OPORTUNIDADE ATUALIZADO ---
class OportunidadeSerializer(serializers.ModelSerializer):
    """
    Serializer definitivo para Oportunidade.
    - Usa PrimaryKeyRelatedField para aceitar IDs para escrita (POST/PUT/PATCH).
    - Sobrescreve 'to_representation' para mostrar dados completos para leitura (GET).
    """
    PROBABILIDADE_POR_FASE = {
        'LEAD': 10,
        'CONTATO': 25,
        'VISITA': 50,
        'PROPOSTA': 75,
        'NEGOCIACAO': 90,
        'GANHO': 100,
        'PERDIDO': 0,
    }

    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    imovel = serializers.PrimaryKeyRelatedField(queryset=Imovel.objects.all(), required=False, allow_null=True)
    responsavel = ResponsavelSimplificadoSerializer(read_only=True)
    tarefas = TarefaSerializer(many=True, read_only=True)

    class Meta:
        model = Oportunidade
        fields = [
            'id', 'titulo', 'valor_estimado', 'fase', 'probabilidade',
            'motivo_perda', 'data_criacao', 'fonte',
            'cliente', 'imovel', 'responsavel', 'tarefas',
            'informacoes_adicionais'
        ]
        read_only_fields = ('data_criacao', 'probabilidade')

    def validate_fase(self, value):
        self.initial_data['probabilidade'] = self.PROBABILIDADE_POR_FASE.get(value, 0)
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        cliente_instance = instance.cliente
        representation['cliente'] = {
            'id': cliente_instance.id,
            'nome_completo': getattr(cliente_instance, 'nome_completo', cliente_instance.nome),
        }
        if instance.imovel:
            imovel_instance = instance.imovel
            endereco_completo = f"{imovel_instance.logradouro}, {imovel_instance.bairro}, {imovel_instance.cidade} - {imovel_instance.estado}"
            representation['imovel'] = {
                'id': imovel_instance.id,
                'endereco': endereco_completo,
                'imovel_titulo': imovel_instance.titulo_anuncio,
            }
        return representation

class ClienteSerializer(serializers.ModelSerializer):
    # NOVO: Campo de leitura para garantir que o frontend tenha um nome para exibir
    nome_exibicao = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'tipo_pessoa', 'documento', 'nome', 'rg', 'data_nascimento', 
            'estado_civil', 'profissao', 'razao_social', 'inscricao_estadual',
            'email', 'telefone', 'cep', 'logradouro', 'numero', 'complemento',
            'bairro', 'cidade', 'estado', 'ativo', 'observacoes', 'foto_perfil',
            'preferencias_imovel', 'imobiliaria', 'data_cadastro', 'data_atualizacao',
            'nome_exibicao' # Inclui o novo campo
        ]
        
        extra_kwargs = {
            'imobiliaria': {'read_only': True}
        }

    def get_nome_exibicao(self, obj: Cliente):
        """ Retorna o nome mais apropriado para exibição na lista. """
        if obj.tipo_pessoa == 'JURIDICA' and obj.razao_social:
            return obj.razao_social
        return obj.nome if obj.nome else "Nome não disponível"

    def validate_documento(self, value):
        """Limpa e valida o documento."""
        return apenas_numeros(value)

    # ... (validate method permanece inalterado)
    def validate(self, data):
        """
        Validação customizada baseada no tipo de pessoa.
        """
        tipo_pessoa = data.get('tipo_pessoa', getattr(self.instance, 'tipo_pessoa', None))
        documento = data.get('documento')

        if tipo_pessoa == 'FISICA':
            if documento and len(apenas_numeros(documento)) != 11:
                raise serializers.ValidationError({"documento": "CPF inválido. Deve conter 11 dígitos."})
        
        elif tipo_pessoa == 'JURIDICA':
            if documento and len(apenas_numeros(documento)) != 14:
                raise serializers.ValidationError({"documento": "CNPJ inválido. Deve conter 14 dígitos."})
            
            razao_social = data.get('razao_social', getattr(self.instance, 'razao_social', None))
            if not razao_social:
                raise serializers.ValidationError({"razao_social": "Razão Social é obrigatória para Pessoa Jurídica."})

        return data

class FunilEtapaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunilEtapa
        fields = ['id', 'titulo', 'ordem', 'probabilidade_fechamento', 'ativa', 'imobiliaria']
        read_only_fields = ['imobiliaria']

# ===================================================================
# Serializers para Relatórios (mantidos como estavam)
# ===================================================================

class FunilVendasSerializer(serializers.Serializer):
    status = serializers.CharField(source='get_status_display')
    total = serializers.IntegerField()

class RelatorioOrigemSerializer(serializers.Serializer):
    origem = serializers.CharField(source='get_origem_display')
    total = serializers.IntegerField()

class RelatorioCorretorSerializer(serializers.ModelSerializer):
    nome_corretor = serializers.ReadOnlyField(source='user.first_name')
    oportunidades_abertas = serializers.IntegerField()
    oportunidades_ganhas = serializers.IntegerField()
    oportunidades_perdidas = serializers.IntegerField()

    class Meta:
        model = PerfilUsuario
        fields = ('id', 'nome_corretor', 'oportunidades_abertas', 'oportunidades_ganhas', 'oportunidades_perdidas')

class RelatorioImobiliariaSerializer(serializers.Serializer):
    sumario_mes_atual = serializers.DictField(
        child=serializers.IntegerField()
    )
    oportunidades_por_mes = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )
# C:\wamp64\www\ImobCloud\app_clientes\serializers.py

from rest_framework import serializers
from .models import Cliente, Visita, Atividade, Oportunidade, Tarefa, FunilEtapa
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
# Adicionámos um serializer para o utilizador e atualizámos o AtividadeSerializer
# para incluir os dados completos do utilizador que registou a atividade.
class UsuarioSimplesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'username']

class AtividadeSerializer(serializers.ModelSerializer):
    # Usamos o serializer acima para mostrar os detalhes do utilizador
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
            'nome_completo': cliente_instance.nome_completo,
        }
        if instance.imovel:
            imovel_instance = instance.imovel
            # CORRIGIDO: O campo de endereço agora é 'logradouro' no modelo
            endereco_completo = f"{imovel_instance.logradouro}, {imovel_instance.bairro}, {imovel_instance.cidade} - {imovel_instance.estado}"
            representation['imovel'] = {
                'id': imovel_instance.id,
                'endereco': endereco_completo,
                'imovel_titulo': imovel_instance.titulo_anuncio,
            }
        return representation

class ClienteSerializer(serializers.ModelSerializer):
    """ Serializer principal para o modelo Cliente. """
    oportunidades = OportunidadeSerializer(many=True, read_only=True)
    visitas = VisitaSerializer(many=True, read_only=True)
    atividades = AtividadeSerializer(many=True, read_only=True)
    tarefas = TarefaSerializer(many=True, read_only=True)
    imobiliaria = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cliente
        # CORREÇÃO AQUI: 'endereco' foi substituído por 'logradouro' e os novos campos foram adicionados.
        fields = [
            'id', 'nome_completo', 'cpf_cnpj', 'email', 'telefone', 'preferencias_imovel', 
            'ativo', 'data_cadastro', 'data_atualizacao', 'data_nascimento', 
            'estado_civil', 'profissao', 'rg', 
            'logradouro', 'numero', 'complemento', 'bairro', # 'endereco' foi substituído por 'logradouro' e 'complemento' foi adicionado.
            'cidade', 'estado', 'cep', 'observacoes', 
            'imobiliaria', 'oportunidades', 'visitas', 'atividades', 'tarefas',
            'foto_perfil', 'inscricao_estadual'
        ]
        
    def create(self, validated_data):
        return super().create(validated_data)

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
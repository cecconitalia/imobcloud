# C:\wamp64\www\ImobCloud\app_clientes\serializers.py

from rest_framework import serializers
# Adicionado EtapaFunil aos imports
from .models import EtapaFunil, Cliente, Visita, Atividade, Oportunidade, Tarefa
from core.models import PerfilUsuario
from app_imoveis.models import Imovel
from django.contrib.auth import get_user_model

User = get_user_model()

# ====================================================================
# NOVO SERIALIZER PARA GERENCIAR AS ETAPAS DO FUNIL
# ====================================================================
class EtapaFunilSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo EtapaFunil, permitindo a gestão das etapas.
    """
    class Meta:
        model = EtapaFunil
        # Incluindo os novos campos para marcar etapas de sucesso/fracasso
        fields = ['id', 'nome', 'ordem', 'e_de_sucesso', 'e_de_fracasso']
        read_only_fields = ['id']

# ====================================================================
# SERIALIZERS SIMPLIFICADOS (INALTERADOS)
# ====================================================================
class ClienteSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome_completo']

class ImovelSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imovel
        fields = ['id', 'titulo_anuncio', 'endereco']

class ResponsavelSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'username']

# ====================================================================
# SERIALIZERS PRINCIPAIS (ATUALIZADOS)
# ====================================================================

class OportunidadeSerializer(serializers.ModelSerializer):
    # Usando os serializadores simplificados para leitura (read-only)
    cliente = ClienteSimplificadoSerializer(read_only=True)
    imovel = ImovelSimplificadoSerializer(read_only=True)
    responsavel = ResponsavelSimplificadoSerializer(read_only=True)
    
    # ATUALIZADO: Mostra os detalhes da etapa do funil na leitura
    fase = EtapaFunilSerializer(read_only=True)
    
    # Campos `*_id` para escrita (write-only)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source='cliente', write_only=True
    )
    imovel_id = serializers.PrimaryKeyRelatedField(
        queryset=Imovel.objects.all(), source='imovel', write_only=True, required=False, allow_null=True
    )
    responsavel_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='responsavel', write_only=True, required=False
    )
    # ATUALIZADO: Campo para definir a fase durante o PATCH/UPDATE
    fase_id = serializers.PrimaryKeyRelatedField(
        queryset=EtapaFunil.objects.all(), source='fase', write_only=True, required=False
    )

    class Meta:
        model = Oportunidade
        fields = [
            'id', 'titulo', 'valor_estimado', 'fonte', 'probabilidade',
            'data_proximo_contato', 'motivo_perda', 'data_criacao', 
            # Campos de leitura
            'cliente', 'imovel', 'responsavel', 'fase',
            # Campos de escrita
            'cliente_id', 'imovel_id', 'responsavel_id', 'fase_id'
        ]
        read_only_fields = ('data_criacao',)

    def validate_fase_id(self, value):
        # Garante que a etapa selecionada pertença à mesma imobiliária da oportunidade
        if 'request' in self.context:
            tenant = self.context['request'].tenant
            if value.imobiliaria != tenant:
                raise serializers.ValidationError("Esta etapa do funil não pertence à sua imobiliária.")
        return value


class VisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visita
        fields = '__all__'


class AtividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atividade
        fields = '__all__'


class TarefaSerializer(serializers.ModelSerializer):
    # Estrutura original mantida
    oportunidade_titulo = serializers.ReadOnlyField(source='oportunidade.titulo')
    cliente_nome = serializers.ReadOnlyField(source='oportunidade.cliente.nome_completo')
    responsavel_nome = serializers.ReadOnlyField(source='responsavel.first_name')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Tarefa
        fields = [
            'id', 'descricao', 'data_criacao', 'data_conclusao', 'concluida', 
            'oportunidade', 'responsavel',
            'oportunidade_titulo', 'cliente_nome', 'responsavel_nome', 'status_display'
        ]
        extra_kwargs = {
            'oportunidade': {'required': False, 'allow_null': True}
        }

    def get_status_display(self, obj):
        if obj.concluida:
            return 'Concluída'
        return 'Pendente'


class ClienteSerializer(serializers.ModelSerializer):
    # Relações aninhadas mantidas
    visitas = VisitaSerializer(many=True, read_only=True)
    atividades = AtividadeSerializer(many=True, read_only=True)
    oportunidades = OportunidadeSerializer(many=True, read_only=True)
    tarefas = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = '__all__'
    
    def get_tarefas(self, obj):
        # Pega tarefas ligadas diretamente às oportunidades do cliente
        tarefas = Tarefa.objects.filter(oportunidade__cliente=obj)
        return TarefaSerializer(tarefas, many=True).data


# ====================================================================
# SERIALIZERS PARA RELATÓRIOS (ATUALIZADOS)
# ====================================================================

class FunilVendasSerializer(serializers.Serializer):
    # ATUALIZADO: Agora espera o nome da fase vindo da anotação na view
    nome_fase = serializers.CharField()
    total = serializers.IntegerField()


class RelatorioOrigemSerializer(serializers.Serializer):
    # ATUALIZADO: A fonte agora vem do modelo Oportunidade
    fonte = serializers.CharField()
    total = serializers.IntegerField()


class RelatorioCorretorSerializer(serializers.ModelSerializer):
    # Estrutura mantida, a lógica de cálculo foi atualizada na view
    nome_corretor = serializers.ReadOnlyField(source='user.get_full_name')
    oportunidades_ganhas = serializers.IntegerField(read_only=True)
    oportunidades_perdidas = serializers.IntegerField(read_only=True)

    class Meta:
        model = PerfilUsuario
        fields = ('id', 'nome_corretor', 'oportunidades_ganhas', 'oportunidades_perdidas')


class RelatorioImobiliariaSerializer(serializers.Serializer):
    # Estrutura mantida, a lógica de cálculo foi atualizada na view
    sumario_mes_atual = serializers.DictField(
        child=serializers.IntegerField()
    )
    oportunidades_por_mes = serializers.ListField(
        child=serializers.DictField()
    )
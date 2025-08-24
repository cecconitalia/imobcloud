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

class AtividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atividade
        fields = '__all__'

class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = '__all__'

# --- SERIALIZER DE OPORTUNIDADE ATUALIZADO ---
class OportunidadeSerializer(serializers.ModelSerializer):
    """
    Serializer definitivo para Oportunidade.
    - Usa PrimaryKeyRelatedField para aceitar IDs para escrita (POST/PUT/PATCH).
    - Sobrescreve 'to_representation' para mostrar dados completos para leitura (GET).
    """
    # NOVO: Dicionário para mapear fases a probabilidades
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
            'motivo_perda', 'informacoes_adicionais', 'data_criacao',
            'cliente', 'imovel', 'responsavel', 'tarefas',
        ]
        read_only_fields = ('data_criacao', 'probabilidade') # A probabilidade será definida pelo backend

    def validate_fase(self, value):
        """
        Define a probabilidade de fechamento automaticamente com base na fase.
        """
        self.initial_data['probabilidade'] = self.PROBABILIDADE_POR_FASE.get(value, 0)
        return value

    def to_representation(self, instance):
        """
        Customiza a saída (JSON) para requisições GET.
        Aqui, transformamos os IDs de volta em objetos completos para o frontend.
        """
        representation = super().to_representation(instance)

        cliente_instance = instance.cliente
        representation['cliente'] = {
            'id': cliente_instance.id,
            'nome_completo': cliente_instance.nome_completo,
        }

        if instance.imovel:
            imovel_instance = instance.imovel
            # CORREÇÃO AQUI: Criar o endereço a partir dos campos disponíveis
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
        # AQUI ESTÁ A ALTERAÇÃO: Adicionando os novos campos
        fields = [
            'id', 'nome_completo', 'cpf_cnpj', 'email', 'telefone', 'preferencias_imovel', 
            'ativo', 'data_cadastro', 'data_atualizacao', 'data_nascimento', 
            'estado_civil', 'profissao', 'rg', 'endereco', 'numero', 'bairro', 
            'cidade', 'estado', 'cep', 'observacoes', 
            'imobiliaria', 'oportunidades', 'visitas', 'atividades', 'tarefas'
        ]
        
    def create(self, validated_data):
        return super().create(validated_data)

# --- SERIALIZER PARA O NOVO MODELO DE ETAPAS ---
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
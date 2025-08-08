# C:\wamp64\www\ImobCloud\app_clientes\serializers.py

from rest_framework import serializers
from .models import Cliente, Visita, Atividade, Oportunidade, Tarefa
from core.models import PerfilUsuario
from app_imoveis.models import Imovel
from django.contrib.auth import get_user_model

User = get_user_model()

# Serializadores simples para representar os dados relacionados de forma segura
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

class OportunidadeSerializer(serializers.ModelSerializer):
    # Usando os serializadores simplificados para representar as relações
    cliente = ClienteSimplificadoSerializer(read_only=True)
    imovel = ImovelSimplificadoSerializer(read_only=True)
    responsavel = ResponsavelSimplificadoSerializer(read_only=True)
    
    # IDs para escrita (para não precisar de enviar objetos complexos)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source='cliente', write_only=True
    )
    imovel_id = serializers.PrimaryKeyRelatedField(
        queryset=Imovel.objects.all(), source='imovel', write_only=True, required=False, allow_null=True
    )
    responsavel_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='responsavel', write_only=True
    )

    class Meta:
        model = Oportunidade
        fields = [
            'id', 'titulo', 'valor_estimado', 'fase', 'fonte', 'probabilidade',
            'data_proximo_contato', 'motivo_perda', 'data_criacao', 'cliente', 'imovel', 'responsavel',
            'cliente_id', 'imovel_id', 'responsavel_id'
        ]
        read_only_fields = ('data_criacao',)


class VisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visita
        fields = '__all__'

class AtividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atividade
        fields = '__all__'

class TarefaSerializer(serializers.ModelSerializer):
    # CORREÇÃO: Campos de modelos relacionados
    oportunidade_titulo = serializers.ReadOnlyField(source='oportunidade.titulo')
    cliente_nome = serializers.ReadOnlyField(source='oportunidade.cliente.nome_completo')
    responsavel_nome = serializers.ReadOnlyField(source='responsavel.first_name')
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Tarefa
        # CORREÇÃO: Lista completa de campos explícitos para evitar o erro
        fields = [
            'id', 'descricao', 'data_criacao', 'data_conclusao', 'concluida', 
            'oportunidade', 'oportunidade_id', 'responsavel', 'responsavel_id',
            'oportunidade_titulo', 'cliente_nome', 'responsavel_nome', 'status_display'
        ]
        # CORREÇÃO: Adicionada a meta para tornar o campo 'oportunidade' não obrigatório no serializer
        extra_kwargs = {
            'oportunidade': {'required': False, 'allow_null': True}
        }

    def get_status_display(self, obj):
        if obj.concluida:
            return 'Concluída'
        return 'Pendente'

class ClienteSerializer(serializers.ModelSerializer):
    visitas = VisitaSerializer(many=True, read_only=True)
    atividades = AtividadeSerializer(many=True, read_only=True)
    oportunidades = OportunidadeSerializer(many=True, read_only=True)
    tarefas = TarefaSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'

# Serializers para Relatórios
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
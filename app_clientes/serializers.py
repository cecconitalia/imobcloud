from rest_framework import serializers
from .models import Cliente, Visita, Atividade, Oportunidade, Tarefa
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

class OportunidadeSerializer(serializers.ModelSerializer):
    """
    Serializer definitivo para Oportunidade.
    - Usa PrimaryKeyRelatedField para aceitar IDs para escrita (POST/PUT/PATCH).
    - Sobrescreve 'to_representation' para mostrar dados completos para leitura (GET).
    """
    # CORREÇÃO: Estes campos agora aceitam IDs para escrita.
    # O queryset garante que o ID fornecido seja válido.
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    imovel = serializers.PrimaryKeyRelatedField(queryset=Imovel.objects.all(), required=False, allow_null=True)
    
    # O responsável é um usuário, não um PerfilUsuario. Corrigindo o queryset.
    # O campo é desabilitado no frontend, então marcamos como read_only aqui
    # para evitar que seja alterado diretamente.
    responsavel = ResponsavelSimplificadoSerializer(read_only=True)
    
    # Este campo continua como apenas leitura, pois as tarefas são gerenciadas separadamente.
    tarefas = TarefaSerializer(many=True, read_only=True)

    class Meta:
        model = Oportunidade
        fields = [
            'id', 'titulo', 'valor_estimado', 'fase', 'fonte', 'probabilidade',
            'motivo_perda', 'data_criacao',
            # Campos de relacionamento
            'cliente', 'imovel', 'responsavel', 'tarefas',
        ]
        read_only_fields = ('data_criacao',)

    def to_representation(self, instance):
        """
        Customiza a saída (JSON) para requisições GET.
        Aqui, transformamos os IDs de volta em objetos completos para o frontend.
        """
        # Pega a representação padrão (que terá os IDs para cliente e imovel)
        representation = super().to_representation(instance)

        # Substitui o ID do cliente pelo objeto completo do cliente
        cliente_instance = instance.cliente
        representation['cliente'] = {
            'id': cliente_instance.id,
            'nome_completo': cliente_instance.nome_completo,
            # Adicione outros campos do cliente se necessário no frontend
        }

        # Se houver um imóvel, substitui o ID pelo objeto do imóvel
        if instance.imovel:
            imovel_instance = instance.imovel
            representation['imovel'] = {
                'id': imovel_instance.id,
                'endereco': imovel_instance.endereco,
                # Adicione outros campos do imóvel se necessário
            }
        
        return representation


class ClienteSerializer(serializers.ModelSerializer):
    """ Serializer principal para o modelo Cliente. """
    # Usa o OportunidadeSerializer revisado para aninhar as oportunidades
    oportunidades = OportunidadeSerializer(many=True, read_only=True)
    visitas = VisitaSerializer(many=True, read_only=True)
    atividades = AtividadeSerializer(many=True, read_only=True)
    tarefas = TarefaSerializer(many=True, read_only=True)
    imobiliaria = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'
    
    def create(self, validated_data):
        return super().create(validated_data)

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
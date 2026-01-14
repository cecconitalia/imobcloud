# C:\wamp64\www\ImobCloud\app_clientes\serializers.py

from rest_framework import serializers
from .models import Cliente, Visita, Atividade, Oportunidade, Tarefa, FunilEtapa, apenas_numeros
from core.models import PerfilUsuario
from app_imoveis.models import Imovel
from django.contrib.auth import get_user_model

User = get_user_model()

# ===================================================================
# Serializers Auxiliares
# ===================================================================

class ResponsavelSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'username']

class UsuarioSimplesSerializer(serializers.ModelSerializer):
    """Usado para preencher comboboxes de usuários"""
    nome_completo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'nome_completo']

    def get_nome_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class ClienteSimplesSerializer(serializers.ModelSerializer):
    """Para exibir dados básicos do cliente em listagens e selects"""
    class Meta:
        model = Cliente
        fields = ['id', 'nome', 'razao_social', 'telefone', 'email']

class ImovelSimplesSerializer(serializers.ModelSerializer):
    """Para exibir dados básicos do imóvel na visita"""
    class Meta:
        model = Imovel
        fields = ['id', 'titulo_anuncio', 'codigo_referencia', 'logradouro', 'numero', 'bairro', 'cidade', 'estado']

# ===================================================================
# Serializers Principais
# ===================================================================

class VisitaSerializer(serializers.ModelSerializer):
    # Escrita: Cliente é ID obrigatório
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    
    # Escrita: Imóveis é uma LISTA de IDs (Write Only)
    imoveis = serializers.PrimaryKeyRelatedField(
        queryset=Imovel.objects.all(), 
        many=True, 
        write_only=True
    )
    
    # Leitura: Objetos completos aninhados
    cliente_obj = ClienteSimplesSerializer(source='cliente', read_only=True)
    # Retorna uma lista de objetos de imóvel na leitura
    imoveis_obj = ImovelSimplesSerializer(source='imoveis', many=True, read_only=True)
    
    corretor_nome = serializers.SerializerMethodField()

    class Meta:
        model = Visita
        fields = [
            'id', 'imobiliaria', 'cliente', 'cliente_obj', 
            'corretor', 'corretor_nome',
            'imoveis', 'imoveis_obj',
            'data_visita', 'status', 'observacoes', 
            'assinatura_cliente', 'data_assinatura', 'assinatura_corretor',
            # 'criado_em', 'atualizado_em' -> Removidos pois não existem no Model Visita padrão
        ]
        read_only_fields = ['imobiliaria', 'assinatura_cliente', 'data_assinatura', 'assinatura_corretor']

    def get_corretor_nome(self, obj):
        if obj.corretor:
            return obj.corretor.get_full_name() or obj.corretor.username
        return "N/A"

class AtividadeSerializer(serializers.ModelSerializer):
    registrado_por_obj = UsuarioSimplesSerializer(source='registrado_por', read_only=True)
    registrado_por_nome = serializers.SerializerMethodField()

    class Meta:
        model = Atividade
        fields = [
            'id', 'tipo', 'descricao', 'data_criacao', 
            'registrado_por', 'registrado_por_obj', 'registrado_por_nome', 
            'cliente'
        ]
        read_only_fields = ['registrado_por', 'data_criacao']

    def get_registrado_por_nome(self, obj):
        return obj.registrado_por.get_full_name() if obj.registrado_por else 'Sistema'

class TarefaSerializer(serializers.ModelSerializer):
    # Campos de Leitura (Display)
    cliente = ClienteSimplesSerializer(source='oportunidade.cliente', read_only=True)
    cliente_nome = serializers.SerializerMethodField()
    responsavel_nome = serializers.SerializerMethodField()
    
    # Campos de Escrita (Inputs via ID)
    responsavel_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='responsavel', write_only=True, required=False, allow_null=True
    )
    oportunidade_id = serializers.PrimaryKeyRelatedField(
        queryset=Oportunidade.objects.all(), source='oportunidade', write_only=True, required=False, allow_null=True
    )
    # Campo auxiliar se quiser ligar cliente diretamente no futuro (sem oportunidade)
    cliente_id_input = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Tarefa
        fields = [
            'id', 'titulo', 'descricao', 'data_vencimento', 'concluida', 
            'status', 'prioridade', # Novos campos do Kanban
            'oportunidade', 'oportunidade_id',
            'responsavel', 'responsavel_id', 'responsavel_nome',
            'cliente', 'cliente_nome', 'cliente_id_input',
            'google_calendar_event_id', 'observacoes_finalizacao',
            'data_criacao' # Corrigido: usa data_criacao em vez de criado_em
        ]
        read_only_fields = ['data_criacao', 'imobiliaria', 'responsavel', 'oportunidade']

    def get_cliente_nome(self, obj):
        if obj.oportunidade and obj.oportunidade.cliente:
            return obj.oportunidade.cliente.nome
        return None

    def get_responsavel_nome(self, obj):
        if obj.responsavel:
            return f"{obj.responsavel.first_name} {obj.responsavel.last_name}".strip() or obj.responsavel.username
        return "Sem responsável"

class OportunidadeSerializer(serializers.ModelSerializer):
    PROBABILIDADE_POR_FASE = {
        'LEAD': 10, 'CONTATO': 25, 'VISITA': 50,
        'PROPOSTA': 75, 'NEGOCIACAO': 90, 'GANHO': 100, 'PERDIDO': 0,
    }

    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    imovel = serializers.PrimaryKeyRelatedField(queryset=Imovel.objects.all(), required=False, allow_null=True)
    responsavel = ResponsavelSimplificadoSerializer(read_only=True)
    tarefas = TarefaSerializer(many=True, read_only=True)
    
    responsavel_nome = serializers.SerializerMethodField()
    imovel_titulo = serializers.SerializerMethodField()

    class Meta:
        model = Oportunidade
        fields = [
            'id', 'titulo', 'valor_estimado', 'fase', 'probabilidade',
            'motivo_perda', 'data_criacao', 'fonte',
            'cliente', 'imovel', 'imovel_titulo', 'responsavel', 'responsavel_nome', 'tarefas',
            'informacoes_adicionais'
        ]
        read_only_fields = ('data_criacao', 'probabilidade', 'imobiliaria')

    def validate_fase(self, value):
        self.initial_data['probabilidade'] = self.PROBABILIDADE_POR_FASE.get(value, 0)
        return value

    def get_responsavel_nome(self, obj):
        return obj.responsavel.get_full_name() if obj.responsavel else 'Não atribuído'

    def get_imovel_titulo(self, obj):
        return str(obj.imovel) if obj.imovel else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Injeta dados ricos do cliente para listagem
        cliente_instance = instance.cliente
        representation['cliente_detalhe'] = {
            'id': cliente_instance.id,
            'nome': cliente_instance.nome,
            'telefone': cliente_instance.telefone,
            'email': cliente_instance.email
        }
        return representation

class ClienteSerializer(serializers.ModelSerializer):
    nome_exibicao = serializers.SerializerMethodField()
    perfil_cliente = serializers.JSONField(required=False)
    
    class Meta:
        model = Cliente
        fields = [
            'id', 'tipo_pessoa', 'documento', 'nome', 'rg', 'data_nascimento', 
            'estado_civil', 'profissao', 'razao_social', 'inscricao_estadual',
            'email', 'telefone', 'cep', 'logradouro', 'numero', 'complemento',
            'bairro', 'cidade', 'estado', 'ativo', 'observacoes', 'foto_perfil',
            'preferencias_imovel', 'imobiliaria', 'data_cadastro', 'data_atualizacao',
            'nome_exibicao', 'perfil_cliente'
        ]
        extra_kwargs = {
            'imobiliaria': {'read_only': True}
        }

    def get_nome_exibicao(self, obj: Cliente):
        if obj.tipo_pessoa == 'JURIDICA' and obj.razao_social:
            return obj.razao_social
        return obj.nome if obj.nome else "Nome não disponível"

    def validate_documento(self, value):
        if value:
            return apenas_numeros(value)
        return value

    def validate(self, data):
        tipo_pessoa = data.get('tipo_pessoa', getattr(self.instance, 'tipo_pessoa', None))
        documento = data.get('documento')
        razao_social = data.get('razao_social')

        # Validações básicas de documento (CPF/CNPJ)
        if tipo_pessoa == 'FISICA':
            if documento and len(apenas_numeros(documento)) != 11:
                # Opcional: raise serializers.ValidationError({"documento": "CPF inválido."})
                pass
        elif tipo_pessoa == 'JURIDICA':
            if documento and len(apenas_numeros(documento)) != 14:
                # Opcional: raise serializers.ValidationError({"documento": "CNPJ inválido."})
                pass
            if not razao_social and not self.instance: # Exige razao social no cadastro PJ
                raise serializers.ValidationError({"razao_social": "Razão Social é obrigatória para Pessoa Jurídica."})
        
        return data

class FunilEtapaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunilEtapa
        fields = ['id', 'titulo', 'ordem', 'probabilidade_fechamento', 'ativa', 'imobiliaria']
        read_only_fields = ['imobiliaria']

# ===================================================================
# Serializers de Relatórios
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
    sumario_mes_atual = serializers.DictField(child=serializers.IntegerField())
    oportunidades_por_mes = serializers.ListField(child=serializers.DictField(child=serializers.IntegerField()))
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from .models import PerfilUsuario, Notificacao, Imobiliaria, ConfiguracaoGlobal, Plano

# Obtém o modelo de usuário ativo (PerfilUsuario)
User = get_user_model()

# ==============================================================================
# SERIALIZERS AUXILIARES (Grupos e Permissões)
# ==============================================================================
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']

# ==============================================================================
# SERIALIZERS DA IMOBILIÁRIA (TENANT)
# ==============================================================================
class ImobiliariaSerializer(serializers.ModelSerializer):
    """
    Serializer completo da imobiliária.
    Inclui campos de identidade visual, endereço, configurações de IA, Redes Sociais e Responsável.
    """
    # Garante o retorno da URL completa e permite upload/null
    foto_perfil = serializers.ImageField(required=False, allow_null=True)
    logo = serializers.ImageField(required=False, allow_null=True)
    
    # Campo calculado (property no model)
    endereco_completo = serializers.ReadOnlyField()

    class Meta:
        model = Imobiliaria
        fields = [
            'id', 'uuid', 'nome_fantasia', 'razao_social', 'cnpj', 'creci', 'tipo_pessoa',
            'logo', 'foto_perfil', 'cor_primaria', 'subdominio', 'voz_da_marca_preferida',
            'email_contato', 'telefone', 'telefone_celular', 'whatsapp', 'website',
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
            'responsavel_nome', 'responsavel_cpf', 'responsavel_email', 'responsavel_telefone',
            'facebook', 'instagram', 'linkedin',
            'facebook_app_id', 'facebook_app_secret', 
            'facebook_page_id', 'facebook_page_access_token', 'facebook_user_access_token',
            'instagram_business_account_id',
            'google_gemini_api_key',
            'data_cadastro', 'endereco_completo'  # CORRIGIDO: data_criacao -> data_cadastro
        ]
        read_only_fields = ['id', 'uuid', 'data_cadastro', 'subdominio'] # CORRIGIDO: data_criacao -> data_cadastro

class ImobiliariaPublicSerializer(serializers.ModelSerializer):
    """
    Usado para exibir dados públicos da imobiliária (site, footer).
    Remove dados sensíveis (tokens, chaves API).
    """
    class Meta:
        model = Imobiliaria
        fields = [
            'nome_fantasia', 'cor_primaria', 'foto_perfil', 'logo',
            'telefone', 'telefone_celular', 'whatsapp', 'email_contato',
            'logradouro', 'numero', 'bairro', 'cidade', 'estado', 'cep', 'creci',
            'facebook', 'instagram', 'linkedin', 'website', 'endereco_completo'
        ]

class ImobiliariaIntegracaoSerializer(serializers.ModelSerializer):
    """
    Serializer específico para atualizar apenas as chaves de integração.
    Usado na view IntegracaoRedesSociaisView.
    """
    class Meta:
        model = Imobiliaria
        fields = [
            'facebook_user_access_token',
            'facebook_page_id',
            'facebook_page_access_token',
            'instagram_business_account_id',
            'google_gemini_api_key',
        ]

# ==============================================================================
# JWT TOKEN CUSTOMIZADO (LOGIN)
# ==============================================================================
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza a resposta do token JWT para incluir informações
    essenciais do usuário e do tenant (imobiliária) no login.
    """
    def validate(self, attrs):
        data = super().validate(attrs)

        # Adiciona dados básicos do usuário
        data['user_name'] = self.user.first_name or self.user.username
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['foto_perfil'] = self.user.foto_perfil.url if self.user.foto_perfil else None

        # Determina o cargo/role
        cargo = 'USER'
        if self.user.is_superuser:
            cargo = 'SUPERADMIN'
        elif self.user.is_admin:
            cargo = 'ADMIN'
        elif self.user.is_corretor:
            cargo = 'CORRETOR'
        data['cargo'] = cargo

        # Dados da Imobiliária (Tenant)
        if hasattr(self.user, 'imobiliaria') and self.user.imobiliaria:
            imob = self.user.imobiliaria
            data['subdomain'] = imob.subdominio
            data['imobiliaria_name'] = imob.nome_fantasia or imob.nome_fantasia
            data['imobiliaria_id'] = imob.id
            data['imobiliaria_cor'] = imob.cor_primaria
            
            # Lógica segura para imagem da empresa (Foto Perfil > Logo > None)
            imobiliaria_foto = None
            try:
                if imob.foto_perfil:
                    imobiliaria_foto = imob.foto_perfil.url
                elif imob.logo:
                    imobiliaria_foto = imob.logo.url
            except Exception:
                pass # Evita erro 500 se o arquivo físico não existir
            
            data['imobiliaria_foto'] = imobiliaria_foto
        else:
            data['subdomain'] = None
            data['imobiliaria_name'] = 'Administração' if self.user.is_superuser else 'Sem Empresa'
            data['imobiliaria_id'] = None
            data['imobiliaria_foto'] = None
            data['imobiliaria_cor'] = '#3B82F6' # Azul padrão

        return data

# ==============================================================================
# SERIALIZERS DE USUÁRIO
# ==============================================================================
class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer principal do usuário (/me).
    Aninha detalhes da imobiliária para uso no frontend store.
    """
    imobiliaria_detalhes = ImobiliariaSerializer(source='imobiliaria', read_only=True)
    nome_completo = serializers.SerializerMethodField()
    imobiliaria_nome = serializers.CharField(source='imobiliaria.nome_fantasia', read_only=True)
    
    groups = GroupSerializer(many=True, read_only=True)
    user_permissions = PermissionSerializer(source='user_permissions', many=True, read_only=True)

    class Meta:
        model = PerfilUsuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'nome_completo', 'foto_perfil', 'is_active', 'is_staff', 'is_superuser',
            'is_admin', 'is_corretor', 'creci', 'telefone',
            'imobiliaria', 'imobiliaria_detalhes', 'imobiliaria_nome',
            'assinatura', 'groups', 'user_permissions', 'google_calendar_token'
        ]
        read_only_fields = ['imobiliaria_detalhes', 'imobiliaria_nome', 'groups', 'user_permissions']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def get_nome_completo(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username

class PublicRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para cadastro público (Self-service).
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'telefone')
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            telefone=validated_data.get('telefone', ''),
            is_active=True
        )
        return user

class CorretorRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para CRUD de usuários pelo Admin.
    """
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    is_admin = serializers.BooleanField(required=False, default=False)
    is_corretor = serializers.BooleanField(required=False, default=True)
    foto_perfil = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'password', 
            'is_admin', 'is_corretor', 'creci', 'telefone', 'assinatura', 'foto_perfil'
        ]
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'id': {'read_only': True}
        }
    
    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Extrai booleans com defaults
        is_admin = validated_data.pop('is_admin', False)
        is_corretor = validated_data.pop('is_corretor', True)
        
        # Define a imobiliária baseada no contexto da requisição (Tenant atual)
        imobiliaria = None
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.imobiliaria:
            imobiliaria = request.user.imobiliaria

        user = User(**validated_data)
        if password:
            user.set_password(password)
        
        user.is_admin = is_admin
        user.is_corretor = is_corretor
        user.imobiliaria = imobiliaria
        user.save()
        return user
    
    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class CorretorDisplaySerializer(serializers.ModelSerializer):
    """
    Serializer leve para listagens de equipe.
    """
    cargo = serializers.SerializerMethodField()
    imobiliaria_nome = serializers.CharField(source='imobiliaria.nome_fantasia', read_only=True)
    nome_completo = serializers.SerializerMethodField()
    foto_perfil = serializers.ImageField(read_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'nome_completo', 'email', 
            'cargo', 'is_admin', 'is_corretor', 'creci', 'telefone', 'assinatura',
            'foto_perfil', 'imobiliaria', 'imobiliaria_nome'
        ]

    def get_cargo(self, obj):
        if obj.is_superuser: return 'Super Admin'
        if obj.is_admin: return 'Administrador'
        if obj.is_corretor: return 'Corretor'
        return 'Usuário'

    def get_nome_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

# ==============================================================================
# OUTROS SERIALIZERS (Notificações, Configurações, Planos)
# ==============================================================================
class NotificacaoSerializer(serializers.ModelSerializer):
    data_criacao_formatada = serializers.SerializerMethodField()

    class Meta:
        model = Notificacao
        fields = ['id', 'titulo', 'mensagem', 'tipo', 'lida', 'data_criacao', 'data_criacao_formatada', 'link']

    def get_data_criacao_formatada(self, obj):
        return obj.data_criacao.strftime("%d/%m/%Y %H:%M")

class ConfiguracaoGlobalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoGlobal
        fields = '__all__'

class PlanoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plano
        fields = '__all__'
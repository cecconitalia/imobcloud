from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from core.models import PerfilUsuario, Notificacao, Imobiliaria, ConfiguracaoGlobal

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
# SERIALIZERS DA IMOBILIÁRIA
# ==============================================================================
class ImobiliariaSerializer(serializers.ModelSerializer):
    """
    Serializer completo da imobiliária, incluindo TODOS os campos.
    Usado para exibir detalhes nas configurações e no contexto do usuário.
    """
    # Garante que a URL da imagem completa seja retornada
    foto_perfil = serializers.ImageField(required=False, allow_null=True)
    # Campo 'logo' mantido para compatibilidade, se necessário
    logo = serializers.ImageField(required=False, allow_null=True)
    # Endereço completo (Property no model)
    endereco_completo = serializers.ReadOnlyField()

    class Meta:
        model = Imobiliaria
        fields = '__all__'
        read_only_fields = ['id', 'uuid', 'data_criacao', 'updated_at']

class ImobiliariaPublicSerializer(serializers.ModelSerializer):
    """
    Usado para exibir dados públicos da imobiliária (site, footer, cabeçalho).
    Filtra dados sensíveis (tokens, chaves API).
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
    Serializer focado apenas nas chaves de integração e tokens sociais.
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
# JWT TOKEN CUSTOMIZADO
# ==============================================================================
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza o serializer de token para adicionar o subdomínio da imobiliária,
    o cargo e o nome do utilizador na resposta do login.
    """
    def validate(self, attrs):
        # Valida e autentica o usuário (self.user é definido aqui)
        data = super().validate(attrs)

        # Adiciona o nome do usuário para ser usado no frontend
        # Tenta pegar o primeiro nome, senão usa o username
        data['user_name'] = self.user.first_name or self.user.username
        data['user_id'] = self.user.id
        data['email'] = self.user.email

        # Lógica para determinar o cargo (Acessando campos diretamente no User)
        cargo = 'USER'
        
        if self.user.is_superuser:
             cargo = 'SUPERADMIN'
        elif self.user.is_admin:
             cargo = 'ADMIN'
        elif self.user.is_corretor:
             cargo = 'CORRETOR'
             
        data['cargo'] = cargo

        # Dados da Imobiliária (Acessando diretamente no User)
        if hasattr(self.user, 'imobiliaria') and self.user.imobiliaria:
            data['subdomain'] = self.user.imobiliaria.subdominio
            # Usa nome fantasia ou razão social ou nome sistema
            data['imobiliaria_name'] = str(self.user.imobiliaria)
            data['imobiliaria_id'] = self.user.imobiliaria.id
            
            # --- CORREÇÃO DO ERRO 500 E COMPATIBILIDADE DE IMAGEM ---
            data['imobiliaria_foto'] = None
            
            try:
                # Tenta 'foto_perfil' (Novo padrão) se existir no objeto e não for nulo
                if hasattr(self.user.imobiliaria, 'foto_perfil') and self.user.imobiliaria.foto_perfil:
                     data['imobiliaria_foto'] = self.user.imobiliaria.foto_perfil.url
                # Tenta 'logo' (Fallback comum) se existir no objeto e não for nulo
                elif hasattr(self.user.imobiliaria, 'logo') and self.user.imobiliaria.logo:
                     data['imobiliaria_foto'] = self.user.imobiliaria.logo.url
            except Exception:
                # Se falhar ao pegar URL (ex: arquivo não encontrado), define como None para não quebrar o login
                data['imobiliaria_foto'] = None

        else:
            data['subdomain'] = None
            data['imobiliaria_name'] = 'Administração' if self.user.is_superuser else 'Sem Empresa'
            data['imobiliaria_id'] = None
            data['imobiliaria_foto'] = None

        return data

# ==============================================================================
# SERIALIZERS DE USUÁRIO
# ==============================================================================
class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer principal do usuário logado (/me).
    Aninha os dados da imobiliária para facilitar o acesso no frontend.
    """
    # Aninha os dados da imobiliária completos
    imobiliaria_detalhes = ImobiliariaSerializer(source='imobiliaria', read_only=True)
    
    # Campo calculado para exibir o nome completo
    nome_completo = serializers.SerializerMethodField()
    
    # Mantendo compatibilidade com código antigo do frontend
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
    Serializer para cadastro público de novos usuários (Self-service).
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'telefone')
    
    def create(self, validated_data):
        # Cria o usuário com senha criptografada usando o manager do User
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            telefone=validated_data.get('telefone', ''),
            is_active=True # Define se o usuário já nasce ativo
        )
        return user

class CorretorRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e atualização de usuários pelo Admin (CRUD de usuários).
    """
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    # Define os campos booleanos com valores padrão caso não sejam enviados
    is_admin = serializers.BooleanField(required=False, default=False)
    is_corretor = serializers.BooleanField(required=False, default=True)
    # Garante que o campo de imagem seja aceito
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
        is_admin = validated_data.pop('is_admin', False)
        is_corretor = validated_data.pop('is_corretor', True)
        
        imobiliaria = None
        request = self.context.get('request')
        if request and hasattr(request, 'tenant'):
            imobiliaria = request.tenant

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
    Serializer leve para listagens de corretores/usuários.
    """
    cargo = serializers.SerializerMethodField()
    imobiliaria_nome = serializers.CharField(source='imobiliaria.nome_fantasia', read_only=True)
    nome_completo = serializers.SerializerMethodField()
    # Garante que o campo de imagem seja serializado corretamente
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
# OUTROS SERIALIZERS (Notificações, Configurações)
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
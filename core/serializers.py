# C:\wamp64\www\ImobCloud\core\serializers.py

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from core.models import PerfilUsuario, Notificacao, Imobiliaria, ConfiguracaoGlobal
from django.db import transaction

# Obtém o modelo de usuário ativo (PerfilUsuario)
User = get_user_model()

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
            data['imobiliaria_name'] = self.user.imobiliaria.nome
            data['imobiliaria_id'] = self.user.imobiliaria.id
            
            # --- CORREÇÃO DO ERRO 500 ---
            # Verifica se o campo 'foto' ou 'logo' existe antes de acessar
            data['imobiliaria_foto'] = None
            
            # Tenta 'foto'
            if hasattr(self.user.imobiliaria, 'foto') and self.user.imobiliaria.foto:
                 data['imobiliaria_foto'] = self.user.imobiliaria.foto.url
            # Tenta 'logo' como fallback (caso o nome do campo seja diferente)
            elif hasattr(self.user.imobiliaria, 'logo') and self.user.imobiliaria.logo:
                 data['imobiliaria_foto'] = self.user.imobiliaria.logo.url

        else:
            data['subdomain'] = None
            data['imobiliaria_name'] = 'Superuser' if self.user.is_superuser else 'N/A'
            data['imobiliaria_id'] = None
            data['imobiliaria_foto'] = None

        return data

# --- SERIALIZERS PARA AVISO FINANCEIRO ---

class ImobiliariaSerializer(serializers.ModelSerializer):
    """
    Serializer completo da imobiliária, incluindo campos financeiros
    para o frontend verificar bloqueios e avisos.
    """
    class Meta:
        model = Imobiliaria
        fields = [
            'id', 'nome', 'subdominio', 'email_contato', 'cnpj', 'creci', 
            'telefone', 'cor_primaria', 'voz_da_marca_preferida',
            # Campos Financeiros Importantes para o Frontend:
            'status_financeiro', 'data_vencimento_atual', 'plano_contratado'
        ]

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer principal do usuário logado (/me).
    Aninha os dados da imobiliária para facilitar o acesso no frontend.
    """
    # Aninha os dados da imobiliária
    imobiliaria_detalhes = ImobiliariaSerializer(source='imobiliaria', read_only=True)
    
    # Campo calculado para exibir o nome completo ou username
    nome_completo = serializers.SerializerMethodField()
    
    # Mantendo compatibilidade com código antigo
    imobiliaria_nome = serializers.CharField(source='imobiliaria.nome', read_only=True)

    class Meta:
        model = PerfilUsuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'nome_completo', 'is_active', 'is_staff', 'is_superuser',
            'is_admin', 'is_corretor', 'creci', 'telefone',
            'imobiliaria', 'imobiliaria_detalhes', 'imobiliaria_nome',
            'assinatura'
        ]
        read_only_fields = ['imobiliaria_detalhes', 'imobiliaria_nome']

    def get_nome_completo(self, obj):
        return obj.get_full_name() or obj.username

class NotificacaoSerializer(serializers.ModelSerializer):
    data_criacao_formatada = serializers.SerializerMethodField()

    class Meta:
        model = Notificacao
        fields = ['id', 'titulo', 'mensagem', 'tipo', 'lida', 'data_criacao', 'data_criacao_formatada', 'link']

    def get_data_criacao_formatada(self, obj):
        return obj.data_criacao.strftime("%d/%m/%Y %H:%M")

class CorretorRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e atualização de usuários (Corretores/Admins).
    """
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    is_admin = serializers.BooleanField(required=False, default=False)
    is_corretor = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'password', 
            'is_admin', 'is_corretor', 'creci', 'telefone', 'assinatura'
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
    Serializer apenas para leitura/exibição de dados do usuário (Endpoint /me).
    """
    cargo = serializers.SerializerMethodField()
    imobiliaria_nome = serializers.CharField(source='imobiliaria.nome', read_only=True)
    
    # Campo de detalhes financeiros da imobiliária
    imobiliaria_detalhes = ImobiliariaSerializer(source='imobiliaria', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 
            'cargo', 'is_admin', 'is_corretor', 'creci', 'telefone', 'assinatura',
            'imobiliaria', 'imobiliaria_nome', 'imobiliaria_detalhes'
        ]

    def get_cargo(self, obj):
        if obj.is_superuser: return 'Super Admin'
        if obj.is_admin: return 'Administrador'
        if obj.is_corretor: return 'Corretor'
        return 'Usuário'

class ImobiliariaIntegracaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imobiliaria
        fields = [
            'facebook_user_access_token',
            'facebook_page_id',
            'facebook_page_access_token',
            'instagram_business_account_id',
        ]
        
class ImobiliariaPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imobiliaria
        fields = ['nome', 'cor_primaria']

class ConfiguracaoGlobalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracaoGlobal
        fields = '__all__'
# C:\wamp64\www\imobcloud\core\serializers.py

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from core.models import PerfilUsuario, Notificacao, Imobiliaria
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
        if self.user.imobiliaria:
            data['subdomain'] = self.user.imobiliaria.subdominio
            # CORREÇÃO: Usa 'nome' pois 'nome_fantasia' não existe no model
            data['imobiliaria_name'] = self.user.imobiliaria.nome
            data['imobiliaria_id'] = self.user.imobiliaria.id
        else:
            data['subdomain'] = None
            data['imobiliaria_name'] = 'Superuser' if self.user.is_superuser else 'N/A'
            data['imobiliaria_id'] = None

        return data

class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = ['id', 'mensagem', 'lida', 'data_criacao', 'link']

class CorretorRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e atualização de usuários (Corretores/Admins).
    Manipula a senha e a associação com a imobiliária (tenant).
    """
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    
    # Campos booleanos explícitos para controle de permissão
    is_admin = serializers.BooleanField(required=False, default=False)
    is_corretor = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'password', 
            'is_admin', 
            'is_corretor', 
            'creci', 
            'telefone', 
            'assinatura'
            # Removido 'foto' pois não existe no model PerfilUsuario
        ]
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'id': {'read_only': True}
        }
    
    @transaction.atomic
    def create(self, validated_data):
        # Remove campos especiais do validated_data para tratar separadamente
        password = validated_data.pop('password', None)
        is_admin = validated_data.pop('is_admin', False)
        is_corretor = validated_data.pop('is_corretor', True)
        
        # Tenta obter a imobiliária do request (middleware tenant)
        # Se for superuser criando sem tenant, isso pode ser None
        imobiliaria = None
        request = self.context.get('request')
        if request and hasattr(request, 'tenant'):
            imobiliaria = request.tenant

        # Cria a instância do usuário mas não salva ainda no banco
        user = User(**validated_data)
        
        # Define a senha com hash
        if password:
            user.set_password(password)
        
        # Define os atributos
        user.is_admin = is_admin
        user.is_corretor = is_corretor
        user.imobiliaria = imobiliaria
        
        user.save()
        
        return user
    
    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Atualiza os campos normais
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        # Se houver senha nova, faz o hash e salva
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance

class CorretorDisplaySerializer(serializers.ModelSerializer):
    """
    Serializer apenas para leitura/exibição de dados do usuário.
    """
    # Usa a property 'cargo_display' do model se existir, ou calcula no frontend
    cargo = serializers.SerializerMethodField()
    # CORREÇÃO: Usa 'nome' em vez de 'nome_fantasia'
    imobiliaria_nome = serializers.CharField(source='imobiliaria.nome', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'cargo', 
            'is_admin', 
            'is_corretor', 
            'creci', 
            'telefone', 
            'assinatura',
            'imobiliaria',
            'imobiliaria_nome'
            # Removido 'foto'
        ]

    def get_cargo(self, obj):
        if obj.is_superuser:
            return 'Super Admin'
        if obj.is_admin:
            return 'Administrador'
        if obj.is_corretor:
            return 'Corretor'
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
        # CORREÇÃO: Ajustado para usar apenas campos existentes no model Imobiliaria
        fields = ['nome', 'cor_primaria']
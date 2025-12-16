# C:\wamp64\www\imobcloud\core\serializers.py

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from core.models import PerfilUsuario, Notificacao, Imobiliaria
from django.db import transaction

User = get_user_model() # PerfilUsuario

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza o serializer de token para adicionar o subdomínio da imobiliária,
    o cargo e o nome do utilizador na resposta do login.
    
    CORRIGIDO: Acessa os campos diretamente, pois PerfilUsuario agora é AbstractUser.
    """
    def validate(self, attrs):
        data = super().validate(attrs) # Valida e autentica o usuário (self.user é setado aqui)

        # Adiciona o nome do usuário para ser usado no frontend
        data['user_name'] = self.user.first_name or self.user.username

        # Lógica para determinar o cargo (Acessando campos diretamente)
        cargo = 'USER'
        
        if self.user.is_superuser:
             cargo = 'SUPERADMIN' # Nome mais claro para superusuario
        elif self.user.is_admin: # Acessando diretamente
             cargo = 'ADMIN'
        elif self.user.is_corretor: # Acessando diretamente
             cargo = 'CORRETOR'
        
        data['cargo'] = cargo

        # Dados da Imobiliária (Acessando campos diretamente)
        if self.user.imobiliaria:
            data['subdomain'] = self.user.imobiliaria.subdominio
            data['imobiliaria_name'] = self.user.imobiliaria.nome
        else:
            data['subdomain'] = None
            data['imobiliaria_name'] = 'Superuser' if self.user.is_superuser else 'N/A'

        return data

# SERIALIZER PARA O MODELO NOTIFICACAO
class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = ['id', 'mensagem', 'lida', 'data_criacao', 'link']


# PerfilUsuarioSerializer agora não é mais um serializer aninhado, 
# mas uma representação dos campos de perfil adicionais. 
# O CorretorRegistrationSerializer irá manipular todos os campos.

# REMOVEMOS O PerfilUsuarioSerializer pois os campos agora estão no User.


class CorretorRegistrationSerializer(serializers.ModelSerializer):
    # Todos os campos de perfil (is_admin, is_corretor, creci, etc.) 
    # estão diretamente no modelo User (PerfilUsuario).

    password = serializers.CharField(write_only=True, min_length=8, required=False)
    
    # Campos customizados para registro (mantidos para clareza)
    is_admin = serializers.BooleanField(required=False)
    is_corretor = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'password', 
            'is_admin', 'is_corretor', 
            'creci', 'telefone', 'assinatura',
            # Adicione aqui outros campos que você deseja permitir no registro
        ]
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'id': {'read_only': True}
        }
    
    @transaction.atomic
    def create(self, validated_data):
        # Campos customizados
        is_admin = validated_data.pop('is_admin', False)
        is_corretor = validated_data.pop('is_corretor', False)
        password = validated_data.pop('password')
        
        # Cria o usuário PerfilUsuario (AbstractUser)
        user = User.objects.create_user(
            **validated_data
        )
        
        # Define os campos customizados (agora que são diretos)
        user.is_admin = is_admin
        user.is_corretor = is_corretor
        user.imobiliaria = self.context['request'].tenant # Associa o tenant
        user.set_password(password)
        user.save()

        # REMOVEMOS: PerfilUsuario.objects.create(user=user, ...)
        
        return user
    
    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Atualiza campos do PerfilUsuario (que é o User)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()

        # REMOVEMOS TODA A LÓGICA DE ATUALIZAÇÃO DO PERFIL SEPARADO
        return instance


class CorretorDisplaySerializer(serializers.ModelSerializer):
    # Mostra os campos diretamente
    cargo = serializers.CharField(source='cargo_display', read_only=True) # Usa o @property do model
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'cargo', 
            'is_admin', 'is_corretor', 'creci', 'telefone', 'assinatura',
            'imobiliaria' # Incluir FK da imobiliária
        ]

class ImobiliariaIntegracaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imobiliaria
        fields = [
            'facebook_user_access_token', # Adicionado de volta
            'facebook_page_id',
            'facebook_page_access_token',
            'instagram_business_account_id',
        ]
        
class ImobiliariaPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imobiliaria
        fields = ['nome', 'cor_primaria']
# C:\wamp64\www\imobcloud\core\serializers.py

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from core.models import PerfilUsuario, Notificacao, Imobiliaria

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza o serializer de token para adicionar o subdomínio da imobiliária,
    o cargo e o nome do utilizador na resposta do login.
    """
    def validate(self, attrs):
        data = super().validate(attrs)

        # Adiciona o nome do usuário para ser usado no frontend
        data['user_name'] = self.user.first_name or self.user.username

        # Lógica para determinar o cargo
        cargo = 'USER'
        
        # Superusuários são sempre ADMIN, independentemente do perfil
        if self.user.is_superuser:
             cargo = 'ADMIN'
        elif hasattr(self.user, 'perfil') and self.user.perfil:
             if self.user.perfil.is_admin:
                 cargo = 'ADMIN'
             elif self.user.perfil.is_corretor:
                 cargo = 'CORRETOR'
        
        data['cargo'] = cargo

        # Dados da Imobiliária
        if hasattr(self.user, 'perfil') and self.user.perfil and self.user.perfil.imobiliaria:
            data['subdomain'] = self.user.perfil.imobiliaria.subdominio
            data['imobiliaria_name'] = self.user.perfil.imobiliaria.nome
        else:
            data['subdomain'] = None
            data['imobiliaria_name'] = 'Superuser' if self.user.is_superuser else 'N/A'

        return data

# SERIALIZER PARA O MODELO NOTIFICACAO
class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = ['id', 'mensagem', 'lida', 'data_criacao', 'link']


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = [
            'is_admin', 'is_corretor', 
            'creci', 'telefone', 'endereco_logradouro', 'endereco_numero',
            'endereco_bairro', 'endereco_cidade', 'endereco_estado', 'endereco_cep',
            'observacoes', 'google_json_file', 'google_calendar_token',
            'assinatura'  # Campo adicionado aqui
        ]

class CorretorRegistrationSerializer(serializers.ModelSerializer):
    perfil = PerfilUsuarioSerializer(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email', 'password', 'perfil']
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'id': {'read_only': True}
        }
    
    def create(self, validated_data):
        perfil_data = validated_data.pop('perfil')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        PerfilUsuario.objects.create(
            user=user,
            imobiliaria=self.context['request'].tenant,
            **perfil_data
        )
        return user
    
    def update(self, instance, validated_data):
        perfil_data = validated_data.pop('perfil', {})
        password = validated_data.pop('password', None)
        
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.email = validated_data.get('email', instance.email)
        if password:
            instance.set_password(password)
        instance.save()
        
        perfil_instance = instance.perfil
        if perfil_data:
            for attr, value in perfil_data.items():
                setattr(perfil_instance, attr, value)
            perfil_instance.save()

        return instance


class CorretorDisplaySerializer(serializers.ModelSerializer):
    perfil = PerfilUsuarioSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email', 'perfil']

class ImobiliariaIntegracaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imobiliaria
        fields = [
            'facebook_page_id',
            'facebook_page_access_token',
            'instagram_business_account_id',
        ]
        
class ImobiliariaPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imobiliaria
        fields = ['nome', 'cor_primaria']
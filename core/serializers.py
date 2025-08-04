from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from core.models import PerfilUsuario # Importa o modelo de PerfilUsuario

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza o serializer de token para adicionar o subdomínio da imobiliária
    e o cargo do utilizador na resposta do login.
    """
    def validate(self, attrs):
        data = super().validate(attrs)

        # Adiciona o subdomínio, o cargo e o nome da imobiliária à resposta se o utilizador tiver um perfil
        if hasattr(self.user, 'perfil') and self.user.perfil and self.user.perfil.imobiliaria:
            data['subdomain'] = self.user.perfil.imobiliaria.subdominio
            data['cargo'] = self.user.perfil.cargo
            # NOVO: Adiciona o nome da imobiliária
            data['imobiliaria_name'] = self.user.perfil.imobiliaria.nome
        else:
            data['subdomain'] = None
            data['cargo'] = 'ADMIN' 
            # NOVO: Valor padrão para o nome da imobiliária
            data['imobiliaria_name'] = 'Superuser' if self.user.is_superuser else 'N/A'


        return data


# Serializer para o registo de corretores
class CorretorRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
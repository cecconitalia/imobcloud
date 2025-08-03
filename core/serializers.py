# C:\wamp64\www\ImobCloud\core\serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Imobiliaria, PerfilUsuario

class ImobiliariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imobiliaria
        fields = ['id', 'nome', 'subdominio'] # Campos básicos que queremos expor

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    imobiliaria = ImobiliariaSerializer(read_only=True) # Serializa a Imobiliária aninhada

    class Meta:
        model = PerfilUsuario
        fields = ['imobiliaria'] # Quais campos do perfil queremos expor

class UserSerializer(serializers.ModelSerializer):
    perfil = PerfilUsuarioSerializer(read_only=True) # Serializa o PerfilUsuario aninhado

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'perfil'] # Campos do usuário
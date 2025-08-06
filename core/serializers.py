from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from core.models import PerfilUsuario

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza o serializer de token para adicionar o subdomínio da imobiliária
    e o cargo do utilizador na resposta do login.
    """
    def validate(self, attrs):
        data = super().validate(attrs)

        if hasattr(self.user, 'perfil') and self.user.perfil and self.user.perfil.imobiliaria:
            data['subdomain'] = self.user.perfil.imobiliaria.subdominio
            data['cargo'] = self.user.perfil.cargo
            data['imobiliaria_name'] = self.user.perfil.imobiliaria.nome
        else:
            data['subdomain'] = None
            data['cargo'] = 'ADMIN'
            data['imobiliaria_name'] = 'Superuser' if self.user.is_superuser else 'N/A'


        return data

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ['cargo', 'creci', 'telefone', 'endereco_logradouro', 'endereco_numero', 'endereco_bairro', 'endereco_cidade', 'endereco_estado', 'endereco_cep', 'observacoes', 'google_json_file']

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
            perfil_instance.cargo = perfil_data.get('cargo', perfil_instance.cargo)
            perfil_instance.creci = perfil_data.get('creci', perfil_instance.creci)
            perfil_instance.telefone = perfil_data.get('telefone', perfil_instance.telefone)
            perfil_instance.endereco_logradouro = perfil_data.get('endereco_logradouro', perfil_instance.endereco_logradouro)
            perfil_instance.endereco_numero = perfil_data.get('endereco_numero', perfil_instance.endereco_numero)
            perfil_instance.endereco_bairro = perfil_data.get('endereco_bairro', perfil_instance.endereco_bairro)
            perfil_instance.endereco_cidade = perfil_data.get('endereco_cidade', perfil_instance.endereco_cidade)
            perfil_instance.endereco_estado = perfil_data.get('endereco_estado', perfil_instance.endereco_estado)
            perfil_instance.endereco_cep = perfil_data.get('endereco_cep', perfil_instance.endereco_cep)
            perfil_instance.observacoes = perfil_data.get('observacoes', perfil_instance.observacoes)
            perfil_instance.google_json_file = perfil_data.get('google_json_file', perfil_instance.google_json_file)
            perfil_instance.save()

        return instance


class CorretorDisplaySerializer(serializers.ModelSerializer):
    perfil = PerfilUsuarioSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'email', 'perfil']
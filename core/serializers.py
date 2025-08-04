from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza o serializer de token para adicionar o subdomínio da imobiliária
    do utilizador na resposta do login.
    """
    def validate(self, attrs):
        # Obtém a resposta padrão (com os tokens access e refresh)
        data = super().validate(attrs)

        # Adiciona o subdomínio à resposta se o utilizador tiver um perfil
        # e pertencer a uma imobiliária.
        if hasattr(self.user, 'perfil_usuario') and self.user.perfil_usuario:
            data['subdomain'] = self.user.perfil_usuario.imobiliaria.subdominio
        else:
            # Para superusers ou utilizadores sem imobiliária associada
            data['subdomain'] = None

        return data
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Substitui a view de token padrão para usar o serializer personalizado que
    inclui o subdomínio na resposta.
    """
    serializer_class = MyTokenObtainPairSerializer
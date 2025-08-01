from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User # Importa o modelo de usu\u00E1rio
from .serializers import UserSerializer # Importa o serializador de usu\u00E1rio

# Este ViewSet lida com opera\u00E7\u00F5es CRUD para o modelo de usu\u00E1rio
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    # A consulta que retorna todos os objetos do modelo de usu\u00E1rio
    queryset = User.objects.all().order_by('-date_joined')
    # O serializador a ser usado para serializar/desserializar os dados
    serializer_class = UserSerializer
    # Permiss\u00F5es: apenas usu\u00E1rios autenticados podem interagir com a API
    permission_classes = [IsAuthenticated]

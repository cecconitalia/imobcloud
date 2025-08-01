# properties/views.py
from rest_framework import viewsets, permissions
from .models import Property
from .serializers import PropertySerializer

class PropertyViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite que os imóveis sejam visualizados ou editados.
    """
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    # Por enquanto, vamos permitir qualquer um acessar. Depois adicionaremos segurança.
    permission_classes = [permissions.AllowAny]
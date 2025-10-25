from rest_framework import serializers
from .models import OpcaoVozDaMarca

class OpcaoVozDaMarcaSerializer(serializers.ModelSerializer):
    """
    Serializa o modelo OpcaoVozDaMarca para ser consumido pela API.
    """
    class Meta:
        model = OpcaoVozDaMarca
        fields = ['id', 'nome', 'descricao']
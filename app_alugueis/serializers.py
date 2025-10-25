# C:\wamp64\www\imobcloud\app_alugueis\serializers.py

from rest_framework import serializers
from .models import Aluguel

class AluguelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluguel
        fields = '__all__'
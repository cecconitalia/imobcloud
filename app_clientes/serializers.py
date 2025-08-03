# C:\wamp64\www\ImobCloud\app_clientes\serializers.py
from rest_framework import serializers
from .models import Cliente, Visita

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ('imobiliaria',) # A imobiliária será definida pelo request.tenant

class VisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visita
        fields = '__all__'
        read_only_fields = ('imobiliaria',) # A imobiliária será definida pelo request.tenant
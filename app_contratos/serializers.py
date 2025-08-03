# C:\wamp64\www\ImobCloud\app_contratos\serializers.py
from rest_framework import serializers
from .models import Contrato

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = '__all__'
        read_only_fields = ('imobiliaria',) # A imobiliária será definida pelo request.tenant
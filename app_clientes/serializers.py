# C:\wamp64\www\ImobCloud\app_clientes\serializers.py
from rest_framework import serializers
from .models import Cliente, Visita, Atividade, Oportunidade # ATUALIZADO: Importar Oportunidade
from app_imoveis.serializers import ImovelDisplaySerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class CorretorDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class AtividadeSerializer(serializers.ModelSerializer):
    registrado_por_obj = CorretorDisplaySerializer(source='registrado_por', read_only=True)

    class Meta:
        model = Atividade
        fields = '__all__'
        read_only_fields = ('cliente', 'registrado_por')


class ClienteDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome_completo', 'cpf_cnpj']

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'
        read_only_fields = ('imobiliaria',)

class VisitaSerializer(serializers.ModelSerializer):
    imovel_obj = ImovelDisplaySerializer(source='imovel', read_only=True)
    cliente_obj = ClienteDisplaySerializer(source='cliente', read_only=True)

    class Meta:
        model = Visita
        fields = '__all__'
        read_only_fields = ('imobiliaria',)
        extra_fields = ['imovel_obj', 'cliente_obj']


# NOVO: Serializer para o Funil de Vendas
class OportunidadeSerializer(serializers.ModelSerializer):
    cliente_obj = ClienteDisplaySerializer(source='cliente', read_only=True)
    imovel_obj = ImovelDisplaySerializer(source='imovel', read_only=True)
    responsavel_obj = CorretorDisplaySerializer(source='responsavel', read_only=True)

    class Meta:
        model = Oportunidade
        fields = '__all__'
        read_only_fields = ('imobiliaria',)
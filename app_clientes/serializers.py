# C:\wamp64\www\ImobCloud\app_clientes\serializers.py
from rest_framework import serializers
from .models import Cliente, Visita, Atividade, Oportunidade, Tarefa
from app_imoveis.serializers import ImovelDisplaySerializer
from django.contrib.auth import get_user_model
from core.models import PerfilUsuario, Imobiliaria

User = get_user_model()

class CorretorDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name']

# NOVO: Serializer para o modelo Tarefa
class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = '__all__'
        read_only_fields = ('oportunidade', 'responsavel')

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

    def create(self, validated_data):
        imobiliaria = self.context['request'].tenant
        if not imobiliaria:
            raise serializers.ValidationError("Imobiliária não identificada para este cliente.")
        
        cliente = Cliente.objects.create(imobiliaria=imobiliaria, **validated_data)
        return cliente


class VisitaSerializer(serializers.ModelSerializer):
    imovel_obj = ImovelDisplaySerializer(source='imovel', read_only=True)
    cliente_obj = ClienteDisplaySerializer(source='cliente', read_only=True)

    class Meta:
        model = Visita
        fields = '__all__'
        read_only_fields = ('imobiliaria',)
        extra_fields = ['imovel_obj', 'cliente_obj']


class OportunidadeSerializer(serializers.ModelSerializer):
    cliente_obj = ClienteDisplaySerializer(source='cliente', read_only=True)
    imovel_obj = ImovelDisplaySerializer(source='imovel', read_only=True)
    responsavel_obj = CorretorDisplaySerializer(source='responsavel', read_only=True)
    # Adiciona as tarefas aninhadas no serializer da oportunidade
    tarefas = TarefaSerializer(many=True, read_only=True)

    class Meta:
        model = Oportunidade
        fields = '__all__'
        read_only_fields = ('imobiliaria',)
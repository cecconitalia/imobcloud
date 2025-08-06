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
        # A 'imobiliaria' é fornecida pela view, então é apenas de leitura aqui.
        read_only_fields = ('imobiliaria',)

    # --- CORREÇÃO APLICADA AQUI ---
    # O método 'create' que causava a duplicação foi removido.
    # A versão padrão do ModelSerializer será usada, que funciona corretamente
    # com a lógica da sua view.


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
    tarefas = TarefaSerializer(many=True, read_only=True)

    class Meta:
        model = Oportunidade
        fields = '__all__'
        read_only_fields = ('imobiliaria',)
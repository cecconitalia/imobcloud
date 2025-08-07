# C:\wamp64\www\ImobCloud\app_clientes\serializers.py

from rest_framework import serializers
from .models import Cliente, Visita, Atividade, Oportunidade, Tarefa
from core.models import PerfilUsuario
from app_imoveis.models import Imovel

# Serializadores simples para representar os dados relacionados de forma segura
class ClienteSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome_completo']

class ImovelSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imovel
        fields = ['id', 'titulo_anuncio', 'endereco']

class ResponsavelSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ['id', 'username']

# CORREÇÃO PRINCIPAL: A view de Oportunidade foi reescrita
class OportunidadeSerializer(serializers.ModelSerializer):
    # Usando os serializadores simplificados para representar as relações
    cliente = ClienteSimplificadoSerializer(read_only=True)
    imovel = ImovelSimplificadoSerializer(read_only=True)
    responsavel = ResponsavelSimplificadoSerializer(read_only=True)
    
    # IDs para escrita (para não precisar de enviar objetos complexos)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source='cliente', write_only=True
    )
    imovel_id = serializers.PrimaryKeyRelatedField(
        queryset=Imovel.objects.all(), source='imovel', write_only=True, required=False, allow_null=True
    )
    responsavel_id = serializers.PrimaryKeyRelatedField(
        queryset=PerfilUsuario.objects.all(), source='responsavel', write_only=True
    )

    class Meta:
        model = Oportunidade
        fields = [
            'id', 'cliente', 'imovel', 'responsavel', 'status_funil', 'data_criacao',
            'cliente_id', 'imovel_id', 'responsavel_id'
        ]
        read_only_fields = ('data_criacao',)


class VisitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visita
        fields = '__all__'

class AtividadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atividade
        fields = '__all__'

class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    visitas = VisitaSerializer(many=True, read_only=True)
    atividades = AtividadeSerializer(many=True, read_only=True)
    oportunidades = OportunidadeSerializer(many=True, read_only=True)
    tarefas = TarefaSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'
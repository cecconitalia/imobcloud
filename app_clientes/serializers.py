# C:\wamp64\www\ImobCloud\app_clientes\serializers.py
from rest_framework import serializers
from .models import Cliente, Visita, Atividade, Oportunidade, Tarefa
# ATUALIZADO: Corrigido o nome do serializer importado
from app_imoveis.serializers import ImovelSerializer 

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class VisitaSerializer(serializers.ModelSerializer):
    # Usando serializers aninhados para exibir informações mais detalhadas
    cliente = serializers.StringRelatedField()
    imovel = serializers.StringRelatedField()

    class Meta:
        model = Visita
        fields = '__all__'

class AtividadeSerializer(serializers.ModelSerializer):
    registrado_por = serializers.StringRelatedField()
    
    class Meta:
        model = Atividade
        fields = '__all__'

class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = '__all__'
        
class OportunidadeSerializer(serializers.ModelSerializer):
    # ATUALIZADO: Usando o serializer correto para exibir os detalhes do imóvel
    imovel = ImovelSerializer(read_only=True)
    cliente = ClienteSerializer(read_only=True)
    responsavel_nome = serializers.CharField(source='responsavel.get_full_name', read_only=True)
    tarefas = TarefaSerializer(many=True, read_only=True)

    class Meta:
        model = Oportunidade
        fields = [
            'id', 
            'titulo', 
            'cliente', 
            'imobiliaria', 
            'responsavel', 
            'responsavel_nome',
            'imovel', 
            'fase', 
            'fonte', 
            'valor_estimado', 
            'data_criacao', 
            'data_fechamento_prevista',
            'tarefas'
        ]
        # Adicionado para permitir que 'responsavel' seja atualizado com um ID
        extra_kwargs = {
            'responsavel': {'write_only': True, 'required': False}
        }
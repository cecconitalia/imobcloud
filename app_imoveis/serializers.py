# C:\wamp64\www\ImobCloud\app_imoveis\serializers.py

from rest_framework import serializers
from .models import Imovel, ImagemImovel, ContatoImovel


class ImagemImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemImovel
        fields = ['id', 'imagem', 'descricao', 'principal']

class ImovelSerializer(serializers.ModelSerializer):
    imagens = ImagemImovelSerializer(many=True, read_only=True)

    class Meta:
        model = Imovel
        fields = '__all__'
        read_only_fields = ('imobiliaria',)

# Esta classe já existe no seu projeto.
class ImovelDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Imovel
        fields = ['id', 'endereco', 'cidade', 'tipo']

# NOVO: Modifique o ContatoImovelSerializer para usar o ImovelDisplaySerializer
class ContatoImovelSerializer(serializers.ModelSerializer):
    imovel_obj = ImovelDisplaySerializer(source='imovel', read_only=True)

    class Meta:
        # ATUALIZADO
        model = ContatoImovel
        fields = ['id', 'imovel', 'imovel_obj', 'nome', 'email', 'telefone', 'mensagem', 'data_contato']
        read_only_fields = ['imovel_obj', 'data_contato']
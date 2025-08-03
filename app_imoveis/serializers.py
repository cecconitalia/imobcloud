# C:\wamp64\www\ImobCloud\app_imoveis\serializers.py
from rest_framework import serializers
from .models import Imovel, ImagemImovel

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

# ESTA CLASSE PRECISA ESTAR PRESENTE E SEM ERROS DE DIGITAÇÃO
class ImovelDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Imovel
        fields = ['id', 'endereco', 'cidade', 'tipo']
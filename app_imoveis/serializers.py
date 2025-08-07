# C:\wamp64\www\ImobCloud\app_imoveis\serializers.py
from rest_framework import serializers
from .models import Imovel, ImagemImovel, ContatoImovel

class ImagemImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemImovel
        fields = ['id', 'imagem', 'descricao', 'principal']

class ImovelSerializer(serializers.ModelSerializer):
    # Serializer aninhado para incluir as imagens na listagem/detalhe do imóvel
    imagens = ImagemImovelSerializer(many=True, read_only=True)

    class Meta:
        model = Imovel
        # '__all__' garante que todos os novos campos do modelo sejam incluídos
        fields = '__all__'

class ContatoImovelSerializer(serializers.ModelSerializer):
    # Adicionando campos read_only para exibir informações do imóvel no painel
    imovel_endereco = serializers.CharField(source='imovel.endereco', read_only=True)
    imovel_cidade = serializers.CharField(source='imovel.cidade', read_only=True)
    
    class Meta:
        model = ContatoImovel
        fields = [
            'id', 
            'imovel', 
            'nome', 
            'email', 
            'telefone', 
            'mensagem', 
            'data_contato', 
            'arquivado',
            'imovel_endereco', # Campo read-only
            'imovel_cidade'    # Campo read-only
        ]
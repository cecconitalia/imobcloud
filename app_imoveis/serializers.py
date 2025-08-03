# C:\wamp64\www\ImobCloud\app_imoveis\serializers.py
from rest_framework import serializers
from .models import Imovel, ImagemImovel

class ImagemImovelSerializer(serializers.ModelSerializer):
    # O campo 'imagem' deve ser um ImageField, que já lida com o upload.
    # Quando você o usa em um ModelSerializer, ele automaticamente espera um arquivo.
    class Meta:
        model = ImagemImovel
        fields = '__all__'
        # Remover read_only_fields = ('imovel',) se você for enviar o imovel_id diretamente
        # Se for enviar o imovel_id no JSON do ImagemImovel, remova 'imovel' do read_only_fields
        # Se for definir o imovel na View, como fizemos, pode manter.

class ImovelSerializer(serializers.ModelSerializer):
    # Permite a criação/atualização de imagens junto com o imóvel
    # O campo 'imagens' agora não é read-only, permite escrita aninhada
    # ATENÇÃO: Para upload de múltiplos arquivos, o ideal é ter um endpoint separado para imagens
    # e não aninhá-los diretamente na criação/atualização do Imovel.
    # No entanto, podemos adaptar para um único upload aqui inicialmente.
    # Por enquanto, manteremos como read_only=True e faremos o upload separado.
    imagens = ImagemImovelSerializer(many=True, read_only=True)

    class Meta:
        model = Imovel
        fields = '__all__'
        read_only_fields = ('imobiliaria',) # A imobiliária será definida pelo request.tenant
# C:\wamp64\www\ImobCloud\app_imoveis\serializers.py

from rest_framework import serializers
from .models import Imovel, ImagemImovel, ContatoImovel

class ImagemImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemImovel
        # Garante que todos os campos necessários são expostos pela API
        fields = ['id', 'imagem', 'principal', 'ordem']

class ContatoImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContatoImovel
        fields = '__all__'

class ImovelSerializer(serializers.ModelSerializer):
    # CORREÇÃO CRÍTICA E DEFINITIVA:
    # Esta linha instrui o serializador a encontrar todos os objetos 'ImagemImovel'
    # relacionados com este imóvel e a usar o 'ImagemImovelSerializer' para os formatar.
    # Sem isto, as imagens nunca seriam enviadas para o frontend.
    imagens = ImagemImovelSerializer(many=True, read_only=True)

    class Meta:
        model = Imovel
        # Adiciona o campo 'imagens' à lista de campos que a API retorna.
        fields = [
            'id', 'titulo_anuncio', 'codigo_referencia', 'tipo', 'finalidade', 'status', 'situacao',
            'publicado_no_site', 'valor_venda', 'valor_aluguel', 'valor_condominio', 'valor_iptu',
            'endereco', 'bairro', 'cidade', 'estado', 'cep', 'area_construida', 'area_util', 'area_total',
            'quartos', 'suites', 'banheiros', 'vagas_garagem', 'lavabo', 'escritorio', 'varanda',
            'mobiliado', 'ar_condicionado', 'moveis_planejados', 'piscina_privativa',
            'churrasqueira_privativa', 'portaria_24h', 'elevador', 'piscina_condominio', 'academia',
            'salao_festas', 'playground', 'quadra_esportiva', 'espaco_pet', 'financiavel',
            'quitado', 'documentacao_ok', 'aceita_pet', 'proprietario', 'numero_matricula',
            'data_captacao', 'data_fim_autorizacao', 'possui_exclusividade', 'comissao_percentual',
            'informacoes_adicionais_autorizacao',
            'imagens'  # O campo 'imagens' PRECISA estar listado aqui.
        ]
        read_only_fields = ('codigo_referencia',)
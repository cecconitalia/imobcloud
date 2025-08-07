from rest_framework import serializers
from .models import Imovel, ImagemImovel, ContatoImovel
from django.conf import settings

class ImagemImovelSerializer(serializers.ModelSerializer):
    imagem = serializers.SerializerMethodField()

    class Meta:
        model = ImagemImovel
        fields = ['id', 'imagem', 'principal', 'ordem']

    def get_imagem(self, obj):
        if obj.imagem:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.imagem.url)
        return None

class ContatoImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContatoImovel
        fields = '__all__'

class ImovelSerializer(serializers.ModelSerializer):
    imagens = ImagemImovelSerializer(many=True, read_only=True)

    class Meta:
        model = Imovel
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
            'imagens'
        ]
        read_only_fields = ('codigo_referencia',)
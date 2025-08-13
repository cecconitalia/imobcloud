# C:\wamp64\www\ImobCloud\app_imoveis\serializers.py

from rest_framework import serializers
from .models import Imovel, ImagemImovel, ContatoImovel

class ImagemImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemImovel
        fields = ['id', 'imagem', 'principal', 'ordem']

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

# --- ADICIONE ESTA NOVA CLASSE NO FINAL DO ARQUIVO ---
class ImovelPublicSerializer(serializers.ModelSerializer):
    """
    Serializer para a visualização pública dos imóveis.
    Expõe apenas os campos necessários e seguros para o público.
    """
    imagens = ImagemImovelSerializer(many=True, read_only=True)
    cidade = serializers.StringRelatedField()
    bairro = serializers.StringRelatedField()

    class Meta:
        model = Imovel
        # Lista de campos que serão visíveis publicamente
        fields = [
            'id', 'codigo_referencia', 'titulo_anuncio', 'tipo', 'finalidade', 'status',
            'valor_venda', 'valor_aluguel', 'valor_condominio', 'valor_iptu',
            'endereco', 'bairro', 'cidade', 'estado',
            'area_util', 'area_construida', 'area_total',
            'quartos', 'suites', 'banheiros', 'vagas_garagem',
            'imagens', 'descricao_completa',
            'piscina_privativa', 'piscina_condominio',
            'churrasqueira_privativa', 'churrasqueira_condominio',
            'academia', 'aceita_pet', 'mobiliado'
        ]
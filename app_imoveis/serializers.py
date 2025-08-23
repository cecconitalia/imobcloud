# app_imoveis/serializers.py

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
    proprietario = serializers.PrimaryKeyRelatedField(
        queryset=Imovel.objects.all(),
        allow_null=True,
        required=False
    )
    
    class Meta:
        model = Imovel
        fields = [
            'id', 'imobiliaria', 'titulo_anuncio', 'codigo_referencia', 'tipo', 'finalidade', 'status', 'situacao',
            'disponibilidade', 'posicao_chave', 'publicado_no_site', 'configuracao_publica',
            'valor_venda', 'valor_aluguel', 'valor_condominio', 'valor_iptu',
            'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'posicao_solar', 'andar', 'vista', 'ponto_referencia',
            'localizacao_condominio', 'area_construida', 'area_util', 'area_total', 'area_terreno', 'dimensao_frente',
            'dimensao_fundos', 'dimensao_direita', 'dimensao_esquerda', 'ano_construcao', 'numero_pavimentos', 'unidades_por_andar',
            'tipo_construcao', 'pe_direito', 'quartos', 'suites', 'banheiros', 'lavabo', 'sala_estar', 'sala_jantar', 'sala_tv',
            'cozinha', 'copa', 'escritorio', 'area_servico', 'despensa', 'closet', 'varanda', 'vagas_garagem', 'vaga_coberta',
            'vaga_privativa', 'portao_eletronico', 'ar_condicionado', 'aquecimento', 'gas_central', 'hidrometro_individual',
            'piso', 'moveis_planejados', 'churrasqueira_privativa', 'piscina_privativa',
            'piscina_condominio', 'churrasqueira_condominio', 'espaco_gourmet', 'playground', 'salao_festas', 'academia',
            'quadra_esportiva', 'sauna', 'espaco_pet', 'portaria_24h', 'elevador', 'vagas_visitantes', 'bicicletario',
            'proprietario', 'numero_matricula', 'data_captacao', 'data_fim_autorizacao', 'possui_exclusividade',
            'comissao_percentual', 'documento_autorizacao', 'informacoes_adicionais_autorizacao', 'financiavel',
            'aceita_permuta', 'quitado', 'documentacao_ok', 'descricao_completa', 'outras_caracteristicas',
            'aceita_pet', 'mobiliado', 'data_cadastro', 'data_atualizacao',
            'imagens',
        ]
        read_only_fields = ('codigo_referencia',)

class ImovelPublicSerializer(serializers.ModelSerializer):
    imagens = ImagemImovelSerializer(many=True, read_only=True)

    class Meta:
        model = Imovel
        fields = [
            'id', 'codigo_referencia', 'titulo_anuncio', 'tipo', 'finalidade', 'status',
            'valor_venda', 'valor_aluguel', 'valor_condominio', 'valor_iptu',
            'logradouro', 'numero', 'bairro', 'cidade', 'estado',
            'area_util', 'area_construida', 'area_total', 'quartos', 'suites', 'banheiros', 'vagas_garagem',
            'imagens', 'descricao_completa', 'aceita_pet', 'mobiliado',
            'piscina_privativa', 'piscina_condominio', 'configuracao_publica',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        config = instance.configuracao_publica or {}
        for field_name, is_visible in config.items():
            if not is_visible:
                representation.pop(field_name, None)
        return representation
# app_imoveis/serializers.py

from rest_framework import serializers
from .models import Imovel, ImagemImovel, ContatoImovel
from app_clientes.serializers import ClienteSerializer
from app_clientes.models import Cliente
from django.db import transaction

class ImagemImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagemImovel
        fields = ['id', 'imagem', 'principal', 'ordem']
        read_only_fields = ['id']


class ImovelSerializer(serializers.ModelSerializer):
    # Campo para LEITURA (read-only): Retorna o objeto completo do cliente.
    proprietario_detalhes = ClienteSerializer(source='proprietario', read_only=True)

    # Campo para ESCRITA (write-only): Aceita apenas o ID de um cliente.
    proprietario = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        required=False, # Não obrigatório ao criar/atualizar imóvel
        allow_null=True, # Permite que seja nulo
        write_only=True # Garante que este campo não será mostrado na resposta GET
    )

    # Campo somente leitura para as imagens, ordenadas pela 'ordem'
    imagens = serializers.SerializerMethodField()

    class Meta:
        model = Imovel
        # Lista explícita de campos para maior clareza para o Serializer base.
        fields = [field.name for field in Imovel._meta.fields] + [
            'imagens',
            'proprietario_detalhes'
        ]
        # O campo 'proprietario' (ID) é automaticamente incluído para escrita por ser 'write_only=True'
        read_only_fields = ('codigo_referencia', 'data_cadastro', 'data_atualizacao', 'imobiliaria')

    def get_imagens(self, obj):
        """
        Retorna as imagens ordenadas corretamente.
        """
        # Acessa o related manager 'imagens' e ordena
        imagens_ordenadas = obj.imagens.order_by('ordem')
        # Serializa a queryset ordenada
        return ImagemImovelSerializer(imagens_ordenadas, many=True).data


class ImovelPublicSerializer(ImovelSerializer):
    """
    Serializer para a visualização pública, omitindo campos sensíveis.
    """
    # Desativa os campos herdados explicitamente
    proprietario = None
    proprietario_detalhes = None

    class Meta:
        model = Imovel
        # CORREÇÃO: Removemos 'ativo' do exclude, pois não existe no modelo Imovel.
        exclude = [
            # 'proprietario', # Desativado acima
            'numero_matricula',
            'data_captacao',
            'data_fim_autorizacao',
            'possui_exclusividade',
            'comissao_percentual',
            'documento_autorizacao',
            'informacoes_adicionais_autorizacao',
            # 'proprietario_detalhes', # Desativado acima
            'imobiliaria',
            # 'ativo', # REMOVIDO - Este campo não existe no modelo Imovel
            'posicao_chave',
            'configuracao_publica',
        ]
        # read_only_fields são herdados implicitamente


class ContatoImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContatoImovel
        fields = '__all__'
        read_only_fields = ('data_criacao',) # Garante que a data não pode ser alterada via API
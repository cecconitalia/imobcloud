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
    # O 'source' aponta para o campo 'proprietario' do modelo Imovel.
    proprietario_detalhes = ClienteSerializer(source='proprietario', read_only=True)
    
    # Campo para ESCRITA (write-only): Aceita apenas o ID de um cliente.
    # O nome 'proprietario' corresponde diretamente ao campo do modelo.
    # A redundância 'source="proprietario"' foi removida.
    proprietario = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        required=False,
        allow_null=True,
        write_only=True # Garante que este campo não será mostrado na resposta GET
    )

    # Campo somente leitura para as imagens
    imagens = ImagemImovelSerializer(many=True, read_only=True)

    class Meta:
        model = Imovel
        # Lista explícita de campos para maior clareza.
        # Incluímos todos os campos do modelo, mais os campos customizados do serializador.
        fields = [field.name for field in Imovel._meta.fields] + [
            'imagens', 
            'proprietario_detalhes'
        ]
        # O campo 'proprietario' (ID) é automaticamente incluído para escrita por ser 'write_only=True'
        read_only_fields = ('codigo_referencia', 'data_cadastro', 'data_atualizacao', 'imobiliaria')


class ImovelPublicSerializer(ImovelSerializer):
    """
    Serializer para a visualização pública, omitindo campos sensíveis.
    """
    class Meta(ImovelSerializer.Meta):
        # Excluímos os campos que não devem aparecer no site público.
        exclude = [
            'proprietario', 'numero_matricula', 'data_captacao', 'data_fim_autorizacao',
            'possui_exclusividade', 'comissao_percentual', 'documento_autorizacao',
            'informacoes_adicionais_autorizacao', 'proprietario_detalhes'
        ]


class ContatoImovelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContatoImovel
        fields = '__all__'
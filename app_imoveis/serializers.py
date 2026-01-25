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
        Retorna as imagens ordenadas corretamente, com URLs absolutas.
        """
        # Acessa o related manager 'imagens' e ordena
        imagens_ordenadas = obj.imagens.order_by('ordem')
        
        # Pega o 'request' do contexto do serializer principal
        request = self.context.get('request')
        
        # Serializa a queryset, passando o 'request' no contexto
        # Isso garante que o ImagemImovelSerializer gere URLs absolutas
        return ImagemImovelSerializer(imagens_ordenadas, many=True, context={'request': request}).data


class ImovelPublicSerializer(serializers.ModelSerializer):
    """
    Serializer para a visualização pública (Portal).
    Inclui dados para redirecionamento e omite dados sensíveis.
    """
    
    # --- NOVOS CAMPOS PARA REDIRECIONAMENTO E UI ---
    subdominio = serializers.CharField(source='imobiliaria.subdominio', read_only=True)
    nome_imobiliaria = serializers.CharField(source='imobiliaria.nome_fantasia', read_only=True)
    imagem_principal = serializers.SerializerMethodField()
    
    # Reutiliza a lógica de imagens do serializer principal
    imagens = serializers.SerializerMethodField()

    class Meta:
        model = Imovel
        # Definimos explicitamente os campos públicos.
        # REMOVIDOS: 'latitude', 'longitude' para corrigir o erro ImproperlyConfigured
        fields = [
            'id', 
            'titulo_anuncio', 
            'descricao_completa',
            'tipo', 
            'status', 
            'finalidade', 
            'valor_venda', 
            'valor_aluguel', 
            'valor_condominio', 
            'valor_iptu',
            'cidade', 
            'bairro', 
            'logradouro', 
            'numero', 
            'cep', 
            'estado', 
            # 'latitude',  <-- REMOVIDO (Não existe no Model)
            # 'longitude', <-- REMOVIDO (Não existe no Model)
            'quartos', 
            'banheiros', 
            'vagas_garagem', 
            'suites', 
            'area_util', 
            'area_total', 
            'area_construida',
            'aceita_pet', 
            'mobiliado', 
            'piscina_privativa', 
            'piscina_condominio', 
            'elevador', 
            'churrasqueira_privativa', 
            'ar_condicionado', 
            'varanda', 
            'academia', 
            'salao_festas', 
            'playground', 
            'portaria_24h',
            'codigo_referencia',
            'imagens',
            # Campos Customizados
            'imagem_principal',
            'subdominio',
            'nome_imobiliaria'
        ]

    def get_imagem_principal(self, obj):
        """Retorna a URL da imagem principal ou a primeira disponível"""
        img = obj.imagens.filter(principal=True).first()
        if not img:
            img = obj.imagens.order_by('ordem').first()
        
        if img and img.imagem:
            try:
                # Retorna URL absoluta se o request estiver no contexto
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(img.imagem.url)
                return img.imagem.url
            except:
                return None
        return None

    def get_imagens(self, obj):
        """Mesma lógica do serializer pai"""
        imagens_ordenadas = obj.imagens.order_by('ordem')
        request = self.context.get('request')
        return ImagemImovelSerializer(imagens_ordenadas, many=True, context={'request': request}).data


# NOVO SERIALIZER PARA AS INFORMAÇÕES RESUMIDAS DO IMÓVEL NO CONTATO
class ImovelResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imovel
        fields = ['id', 'codigo_referencia', 'tipo']


class ContatoImovelSerializer(serializers.ModelSerializer):
    imovel_obj = ImovelResumoSerializer(source='imovel', read_only=True)
    
    class Meta:
        model = ContatoImovel
        fields = [field.name for field in ContatoImovel._meta.fields] + ['imovel_obj']
        read_only_fields = ('data_contato',) 

class ImovelSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imovel
        fields = ['id', 'titulo_anuncio', 'codigo_referencia', 'logradouro', 'numero', 'bairro', 'cidade', 'valor_venda', 'valor_aluguel']
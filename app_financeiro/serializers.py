# C:\wamp64\www\ImobCloud\app_financeiro\serializers.py

from rest_framework import serializers
from .models import Categoria, Conta, Transacao, FormaPagamento
from app_clientes.models import Cliente
from app_imoveis.models import Imovel

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ('imobiliaria',)

class ContaSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Conta
        fields = '__all__'
        read_only_fields = ('imobiliaria',)

class FormaPagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPagamento
        fields = '__all__'
        read_only_fields = ('imobiliaria',)

class TransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = '__all__'
        read_only_fields = ('imobiliaria',)

# ==================================================================
# CORREÇÃO DO ERRO 'nome_completo'
# ==================================================================
class ClienteSimplificadoSerializer(serializers.ModelSerializer):
    """ 
    Serializer simplificado que exibe o nome correto do cliente. 
    (Corrigido para usar 'nome_display' em vez de 'nome_completo')
    """
    nome_display = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        # CORREÇÃO: Trocado 'nome_completo' por 'nome_display'
        # Adicionado 'documento' para consistência
        fields = ['id', 'nome_display', 'documento'] 

    def get_nome_display(self, obj):
        """ Retorna Razão Social para PJ, ou Nome para PF. """
        try:
            if obj.tipo_pessoa == 'JURIDICA' and obj.razao_social:
                return obj.razao_social
        except AttributeError:
            # Lida com casos onde o modelo Cliente pode não ter os campos
            pass
        return obj.nome # Retorna 'nome' como padrão
# ==================================================================


class ImovelSimplificadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imovel
        # 'titulo_anuncio' está correto
        fields = ['id', 'titulo_anuncio']

class TransacaoListSerializer(serializers.ModelSerializer):
    categoria = serializers.StringRelatedField()
    conta = serializers.StringRelatedField()
    forma_pagamento = serializers.StringRelatedField()
    # Agora usa o ClienteSimplificadoSerializer corrigido
    cliente = ClienteSimplificadoSerializer() 
    imovel = ImovelSimplificadoSerializer()
    
    class Meta:
        model = Transacao
        fields = [
            'id', 'descricao', 'valor', 'data_transacao', 'data_vencimento',
            'tipo', 'status', 'categoria', 'conta', 'forma_pagamento',
            'cliente', 'imovel'
        ]
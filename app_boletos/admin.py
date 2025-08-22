# C:\wamp64\www\ImobCloud\app_boletos\admin.py

from django.contrib import admin
from .models import ConfiguracaoBanco, Boleto, ArquivoRemessa, ArquivoRetorno

@admin.register(ConfiguracaoBanco)
class ConfiguracaoBancoAdmin(admin.ModelAdmin):
    list_display = ['imobiliaria', 'nome_banco', 'client_id', 'agencia', 'conta']
    list_filter = ['imobiliaria', 'nome_banco']
    search_fields = ['imobiliaria__nome', 'nome_banco']
    raw_id_fields = ['imobiliaria']

@admin.register(ArquivoRemessa)
class ArquivoRemessaAdmin(admin.ModelAdmin):
    list_display = ('id', 'imobiliaria', 'configuracao_banco', 'data_geracao')
    list_filter = ('imobiliaria', 'configuracao_banco__nome_banco')
    search_fields = ('id', 'arquivo')
    raw_id_fields = ('imobiliaria', 'configuracao_banco')

@admin.register(ArquivoRetorno)
class ArquivoRetornoAdmin(admin.ModelAdmin):
    list_display = ('id', 'imobiliaria', 'configuracao_banco', 'data_processamento')
    list_filter = ('imobiliaria', 'configuracao_banco__nome_banco')
    search_fields = ('id', 'arquivo')
    raw_id_fields = ('imobiliaria', 'configuracao_banco')

@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    # CORREÇÃO: Campos ajustados para refletir os novos modelos
    list_display = ['get_transacao_id', 'nosso_numero', 'status', 'get_data_vencimento', 'data_pagamento', 'valor_pago']
    list_filter = ['status', 'remessa__configuracao_banco__nome_banco']
    search_fields = ['transacao__descricao', 'nosso_numero']
    raw_id_fields = ['transacao', 'remessa', 'retorno']

    # Métodos para exibir campos de modelos relacionados
    def get_transacao_id(self, obj):
        return obj.transacao.id
    get_transacao_id.short_description = 'Transação ID'

    def get_data_vencimento(self, obj):
        return obj.transacao.data_vencimento
    get_data_vencimento.short_description = 'Vencimento'
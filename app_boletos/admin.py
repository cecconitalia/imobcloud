# C:\wamp64\www\ImobCloud\app_boletos\admin.py

from django.contrib import admin
from .models import ConfiguracaoBanco, Boleto

@admin.register(ConfiguracaoBanco)
class ConfiguracaoBancoAdmin(admin.ModelAdmin):
    list_display = ['imobiliaria', 'nome_banco', 'client_id']
    list_filter = ['imobiliaria', 'nome_banco']
    search_fields = ['imobiliaria__nome', 'nome_banco']
    raw_id_fields = ['imobiliaria']

@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = ['transacao', 'status', 'data_vencimento', 'data_pagamento']
    list_filter = ['status', 'configuracao__nome_banco']
    search_fields = ['transacao__descricao', 'codigo_barras']
    raw_id_fields = ['transacao', 'configuracao']
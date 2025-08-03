# app_contratos/admin.py
from django.contrib import admin
from .models import Contrato

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('tipo_contrato', 'imovel', 'cliente', 'valor_total', 'status_contrato', 'data_assinatura', 'imobiliaria')
    list_filter = ('tipo_contrato', 'status_contrato', 'imobiliaria', 'data_assinatura')
    search_fields = ('imovel__endereco', 'cliente__nome_completo', 'condicoes_pagamento')
    raw_id_fields = ('imovel', 'cliente', 'imobiliaria')
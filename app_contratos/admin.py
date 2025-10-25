# Em app_contratos/admin.py

from django.contrib import admin
from .models import Contrato, Pagamento

class PagamentoInline(admin.TabularInline):
    model = Pagamento
    extra = 0
    readonly_fields = ('data_pagamento', 'status')

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'tipo_contrato', 'inquilino', 'proprietario', 'status_contrato', 'data_inicio', 'valor_total')
    list_filter = ('tipo_contrato', 'status_contrato', 'imobiliaria')
    search_fields = ('imovel__titulo_anuncio', 'inquilino__nome_completo', 'proprietario__nome_completo')
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('imobiliaria', 'tipo_contrato', 'status_contrato', 'imovel')
        }),
        ('Partes Envolvidas', {
            'fields': ('inquilino', 'proprietario')
        }),
        ('Valores e Prazos', {
            # *** CORREÇÃO: 'condicoes_pagamento' foi removido daqui ***
            'fields': ('valor_total', 'duracao_meses', 'data_inicio', 'data_fim', 'data_assinatura')
        }),
        ('Outras Informações', {
            'fields': ('informacoes_adicionais',)
        }),
    )
    
    inlines = [PagamentoInline]

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('contrato', 'valor', 'data_vencimento', 'data_pagamento', 'status')
    list_filter = ('status', 'data_vencimento')
    search_fields = ('contrato__imovel__titulo_anuncio',)
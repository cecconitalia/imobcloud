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
        # ==================================================================
        # CORREÇÃO: Adicionando 'fiadores' em 'Partes Envolvidas'
        # Isso garante que o campo ManyToMany seja exibido no Django Admin.
        # ==================================================================
        ('Partes Envolvidas', {
            'fields': ('inquilino', 'proprietario', 'fiadores') # <--- CAMPO ADICIONADO AQUI
        }),
        ('Valores e Prazos', {
            'fields': ('valor_total', 'duracao_meses', 'aluguel', 'data_inicio', 'data_fim', 'data_assinatura')
        }),
        ('Informações de Pagamento', {
            'fields': ('formas_pagamento',) # Adicionado aqui para ter formas_pagamento
        }),
        ('Conteúdo Personalizado', {
            'fields': ('conteudo_personalizado', 'informacoes_adicionais',)
        }),
    )
    
    inlines = [PagamentoInline]

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('contrato', 'valor', 'data_vencimento', 'data_pagamento', 'status')
    list_filter = ('status', 'data_vencimento')
    search_fields = ('contrato__imovel__titulo_anuncio',)
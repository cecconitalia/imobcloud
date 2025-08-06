# app_contratos/admin.py
from django.contrib import admin
from .models import Contrato, Pagamento # ATUALIZADO: Importar Pagamento também

# Inline para exibir pagamentos dentro do detalhe do contrato
class PagamentoInline(admin.TabularInline):
    model = Pagamento
    extra = 0 # Não mostrar formulários de pagamento extras por padrão
    readonly_fields = ('valor', 'data_vencimento', 'data_pagamento', 'status') # Apenas visualização
    can_delete = False

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('tipo_contrato', 'imovel', 'cliente', 'valor_total', 'status_contrato', 'data_assinatura', 'imobiliaria')
    list_filter = ('tipo_contrato', 'status_contrato', 'imobiliaria', 'data_assinatura')
    search_fields = ('imovel__endereco', 'cliente__nome_completo', 'condicoes_pagamento')
    raw_id_fields = ('imovel', 'cliente', 'imobiliaria')
    inlines = [PagamentoInline] # NOVO: Adiciona a visualização de pagamentos

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('contrato', 'valor', 'data_vencimento', 'status', 'data_pagamento')
    list_filter = ('status', 'data_vencimento')
    search_fields = ('contrato__imovel__endereco', 'contrato__cliente__nome_completo')
    raw_id_fields = ('contrato',)
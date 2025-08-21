# C:\wamp64\www\ImobCloud\app_contratos\admin.py

from django.contrib import admin
from .models import Contrato, Pagamento

class PagamentoInline(admin.TabularInline):
    model = Pagamento
    extra = 1

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tipo_contrato', 'imovel', 'inquilino', 'proprietario', 
        'valor_total', 'status_contrato', 'data_inicio', 'data_fim'
    ]
    list_filter = ['tipo_contrato', 'status_contrato']
    search_fields = [
        'imovel__endereco', 'inquilino__nome_completo', 'proprietario__nome_completo'
    ]
    raw_id_fields = ['imovel', 'inquilino', 'proprietario']
    
    fieldsets = (
        ('Informações do Contrato', {
            'fields': (
                'imobiliaria', 'tipo_contrato', 'status_contrato',
                'imovel', 'inquilino', 'proprietario',
                'valor_total', 'condicoes_pagamento'
            )
        }),
        ('Datas e Duração', {
            'fields': (
                'data_assinatura', 'data_inicio', 'data_fim', 'duracao_meses'
            )
        }),
    )

    inlines = [PagamentoInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.tenant:
            queryset = queryset.filter(imobiliaria=request.tenant)
        return queryset

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ['contrato', 'valor', 'data_vencimento', 'status', 'data_pagamento']
    list_filter = ['status', 'data_vencimento']
    search_fields = ['contrato__imovel__endereco', 'contrato__inquilino__nome_completo']
    raw_id_fields = ['contrato']
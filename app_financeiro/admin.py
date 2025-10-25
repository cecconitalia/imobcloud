# C:\wamp64\www\ImobCloud\app_financeiro\admin.py

from django.contrib import admin
# CORREÇÃO: Trocado 'ContaBancaria' por 'Conta'
from .models import Categoria, Conta, Transacao, FormaPagamento

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'imobiliaria')
    list_filter = ('tipo', 'imobiliaria')
    search_fields = ('nome',)

# CORREÇÃO: Trocado 'ContaBancaria' por 'Conta' e ajustado o nome da classe admin
@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'saldo_inicial', 'imobiliaria')
    list_filter = ('imobiliaria',)
    search_fields = ('nome',)

@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'imobiliaria')
    list_filter = ('imobiliaria',)
    search_fields = ('nome',)

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'data_vencimento', 'tipo', 'status', 'imobiliaria')
    list_filter = ('tipo', 'status', 'imobiliaria', 'categoria')
    search_fields = ('descricao', 'cliente__nome', 'imovel__titulo')
    raw_id_fields = ('imobiliaria', 'categoria', 'conta', 'forma_pagamento', 'cliente', 'imovel', 'contrato')
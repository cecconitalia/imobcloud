# app_financeiro/admin.py

from django.contrib import admin
from .models import Categoria, ContaBancaria, Transacao, FormaPagamento

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'imobiliaria']
    list_filter = ['tipo', 'imobiliaria']
    search_fields = ['nome']
    
@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'banco', 'agencia', 'numero_conta', 'saldo_atual', 'imobiliaria', 'ativo']
    list_filter = ['banco', 'ativo']
    search_fields = ['nome', 'banco', 'numero_conta']

@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'imobiliaria', 'ativo']
    list_filter = ['imobiliaria', 'ativo']
    search_fields = ['nome', 'slug']
    prepopulated_fields = {'slug': ('nome',)} # Gera o slug automaticamente
    
@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor', 'tipo', 'data_vencimento', 'status', 'imobiliaria']
    list_filter = ['tipo', 'status', 'imobiliaria']
    search_fields = ['descricao', 'imovel__endereco', 'contrato__inquilino__nome_completo']
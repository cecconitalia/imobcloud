# app_clientes/admin.py
from django.contrib import admin
from .models import Cliente, Visita

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf_cnpj', 'email', 'telefone', 'imobiliaria')
    list_filter = ('imobiliaria',)
    search_fields = ('nome_completo', 'cpf_cnpj', 'email', 'telefone')
    raw_id_fields = ('imobiliaria',)

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'cliente', 'data_hora', 'status', 'imobiliaria')
    list_filter = ('status', 'data_hora', 'imobiliaria')
    search_fields = ('imovel__endereco', 'cliente__nome_completo')
    raw_id_fields = ('imovel', 'cliente', 'imobiliaria')
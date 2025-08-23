# app_imoveis/admin.py

from django.contrib import admin
from .models import Imovel, ImagemImovel, ContatoImovel

# Configuração para exibir imagens inline no admin do Imóvel
class ImagemImovelInline(admin.TabularInline):
    model = ImagemImovel
    extra = 1 # Quantos campos de upload extra mostrar

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    list_display = ('logradouro', 'cidade', 'tipo', 'finalidade', 'status', 'imobiliaria')
    list_filter = ('imobiliaria', 'status', 'tipo', 'cidade')
    search_fields = ('logradouro', 'cidade', 'descricao')
    inlines = [ImagemImovelInline] # Adiciona a gestão de imagens dentro do formulário do imóvel

# NOVA CLASSE ADICIONADA PARA GERIR OS CONTACTOS
@admin.register(ContatoImovel)
class ContatoImovelAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'nome', 'email', 'data_contato')
    list_filter = ('data_contato', 'imovel')
    search_fields = ('nome', 'email', 'mensagem')
    # ATUALIZADO
    readonly_fields = ('imovel', 'nome', 'email', 'telefone', 'mensagem', 'data_contato')

    def has_add_permission(self, request):
        # Impede a criação de novos contatos através do painel de admin
        return False
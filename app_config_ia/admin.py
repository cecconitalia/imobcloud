from django.contrib import admin
from .models import ModeloDePrompt, OpcaoVozDaMarca

@admin.register(OpcaoVozDaMarca)
class OpcaoVozDaMarcaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome', 'descricao')

@admin.register(ModeloDePrompt)
class ModeloDePromptAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para os Modelos de Prompt de IA.
    """
    # Adicionado 'modelo_api' na lista de colunas
    list_display = (
        'nome_do_modelo', 
        'modelo_api', 
        'em_uso_busca',
        'em_uso_descricao',
        'data_atualizacao'
    )
    
    list_filter = ('modelo_api', 'em_uso_busca', 'em_uso_descricao')
    
    # Adicionado 'modelo_api' para edição rápida na lista
    list_editable = ('modelo_api', 'em_uso_busca', 'em_uso_descricao')
    
    search_fields = ('nome_do_modelo', 'template_do_prompt')
    
    ordering = ('-em_uso_busca', '-em_uso_descricao', 'nome_do_modelo')

    # Adicionado 'modelo_api' no formulário de edição
    fieldsets = (
        ('Configuração Principal', {
            'fields': ('nome_do_modelo', 'modelo_api')
        }),
        ('Conteúdo do Prompt', {
            'fields': ('template_do_prompt',)
        }),
        ('Configuração de Uso (Ative apenas um de cada tipo)', {
            'fields': ('em_uso_busca', 'em_uso_descricao')
        }),
    )
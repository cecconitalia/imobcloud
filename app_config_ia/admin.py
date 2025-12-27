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
    list_display = (
        'nome_do_modelo', 
        'em_uso_busca',
        'em_uso_descricao',
        'data_atualizacao'
    )
    
    list_filter = ('em_uso_busca', 'em_uso_descricao')
    
    list_editable = ('em_uso_busca', 'em_uso_descricao')
    
    search_fields = ('nome_do_modelo', 'template_do_prompt')
    
    ordering = ('-em_uso_busca', '-em_uso_descricao', 'nome_do_modelo')

    fieldsets = (
        (None, {
            'fields': ('nome_do_modelo', 'template_do_prompt')
        }),
        ('Configuração de Uso (Ative apenas um de cada tipo)', {
            'fields': ('em_uso_busca', 'em_uso_descricao')
        }),
    )
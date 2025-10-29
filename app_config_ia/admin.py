# app_config_ia/admin.py
from django.contrib import admin
from .models import ModeloDePrompt

@admin.register(ModeloDePrompt)
class ModeloDePromptAdmin(admin.ModelAdmin):
    """
    Configuração do Admin para os Modelos de Prompt de IA.
    """
    
    # CORRIGIDO: Usa os nomes de campos corretos do models.py
    list_display = (
        'nome_do_modelo', 
        'em_uso_busca',        # Corrigido de 'em_uso'
        'em_uso_descricao',    # Novo campo adicionado
        'data_atualizacao'
    )
    
    # CORRIGIDO: Filtra pelos novos campos booleanos
    list_filter = ('em_uso_busca', 'em_uso_descricao')
    
    # CORRIGIDO: Permite editar os novos campos na lista
    list_editable = ('em_uso_busca', 'em_uso_descricao')
    
    # CORRIGIDO: Procura pelo nome de campo correto
    search_fields = ('nome_do_modelo', 'template_do_prompt') # Corrigido de 'nome_referencia'
    
    # CORRIGIDO: Ordena pelos novos campos
    ordering = ('-em_uso_busca', '-em_uso_descricao', 'nome_do_modelo')

    # Adiciona fieldsets para organizar o formulário de edição
    fieldsets = (
        (None, {
            'fields': ('nome_do_modelo', 'template_do_prompt')
        }),
        ('Configuração de Uso (Ative apenas um de cada tipo)', {
            'fields': ('em_uso_busca', 'em_uso_descricao')
        }),
    )
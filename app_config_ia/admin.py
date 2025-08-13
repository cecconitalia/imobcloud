from django.contrib import admin
from .models import ModeloDePrompt, OpcaoVozDaMarca

@admin.register(ModeloDePrompt)
class ModeloDePromptAdmin(admin.ModelAdmin):
    """
    Configura a exibição dos Modelos de Prompt no Django Admin.
    """
    list_display = ('nome_referencia', 'em_uso', 'notas')
    list_filter = ('em_uso',)
    search_fields = ('nome_referencia', 'template_do_prompt')
    list_editable = ('em_uso',)
    ordering = ('-em_uso', 'nome_referencia')


@admin.register(OpcaoVozDaMarca)
class OpcaoVozDaMarcaAdmin(admin.ModelAdmin):
    """
    Configura a exibição das Opções de Voz da Marca no Django Admin.
    """
    list_display = ('nome', 'descricao')
    search_fields = ('nome', 'descricao')
    ordering = ('nome',)
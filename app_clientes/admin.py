# app_clientes/admin.py
from django.contrib import admin
from .models import Cliente, Visita, Oportunidade, Tarefa, Atividade, FunilEtapa

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf_cnpj', 'email', 'telefone', 'imobiliaria')
    list_filter = ('imobiliaria',)
    search_fields = ('nome_completo', 'cpf_cnpj', 'email', 'telefone')
    raw_id_fields = ('imobiliaria',)

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    # ATUALIZADO: Substituído 'data_hora' por 'data_visita' e removido 'status'
    list_display = ('imovel', 'cliente', 'data_visita', 'imobiliaria')
    # ATUALIZADO: Ajustado 'list_filter' para campos válidos
    list_filter = ('imobiliaria', 'data_visita')
    search_fields = ('imovel__endereco', 'cliente__nome_completo')
    raw_id_fields = ('imovel', 'cliente', 'imobiliaria')

@admin.register(Oportunidade)
class OportunidadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'fase', 'valor_estimado', 'responsavel')
    list_filter = ('fase', 'imobiliaria', 'responsavel')
    search_fields = ('titulo', 'cliente__nome_completo')
    raw_id_fields = ('cliente', 'imovel', 'responsavel', 'imobiliaria')

@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'oportunidade', 'responsavel', 'data_vencimento', 'concluida')
    list_filter = ('concluida', 'responsavel', 'data_vencimento')
    search_fields = ('titulo', 'oportunidade__titulo')
    raw_id_fields = ('oportunidade', 'responsavel')

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descricao', 'cliente', 'registrado_por', 'data_criacao')
    list_filter = ('tipo', 'registrado_por')
    search_fields = ('descricao', 'cliente__nome_completo')
    raw_id_fields = ('cliente', 'registrado_por')

@admin.register(FunilEtapa)
class FunilEtapaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'imobiliaria', 'ordem', 'probabilidade_fechamento', 'ativa')
    list_filter = ('imobiliaria', 'ativa')
    search_fields = ('titulo',)
    raw_id_fields = ('imobiliaria',)
    ordering = ('imobiliaria', 'ordem')
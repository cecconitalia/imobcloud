# C:\wamp64\www\ImobCloud\app_clientes\admin.py

from django.contrib import admin
from .models import Cliente, Oportunidade, Atividade, Visita, Tarefa, FunilEtapa
from simple_history.admin import SimpleHistoryAdmin

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # VERSÃO FINAL: com todos os campos e lógicas de exibição
    list_display = ('get_nome_display', 'documento', 'tipo_pessoa', 'email', 'telefone', 'imobiliaria', 'ativo')
    search_fields = ('nome', 'razao_social', 'documento', 'email')
    list_filter = ('imobiliaria', 'ativo', 'tipo_pessoa', 'data_cadastro')
    ordering = ('-data_cadastro',)

    def get_nome_display(self, obj):
        if obj.tipo_pessoa == 'JURIDICA' and obj.razao_social:
            return obj.razao_social
        return obj.nome
    get_nome_display.short_description = 'Nome / Razão Social'
    get_nome_display.admin_order_field = 'nome'


@admin.register(Oportunidade)
class OportunidadeAdmin(SimpleHistoryAdmin):
    list_display = ('titulo', 'cliente', 'imovel', 'fase', 'valor_estimado', 'responsavel', 'imobiliaria')
    # CORREÇÃO: Atualizado para buscar pelo campo correto do imóvel (titulo_anuncio)
    search_fields = ('titulo', 'cliente__nome', 'cliente__razao_social', 'imovel__titulo_anuncio')
    list_filter = ('imobiliaria', 'fase', 'responsavel')
    history_list_display = ["status"]

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo', 'data_criacao', 'registrado_por')
    # VERSÃO FINAL: busca por nome e razão social do cliente
    search_fields = ('cliente__nome', 'cliente__razao_social', 'descricao')
    list_filter = ('tipo', 'data_criacao')

@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    # CORREÇÃO: Trocamos 'imovel' por um método customizado 'get_imoveis'
    list_display = ('cliente', 'get_imoveis', 'data_visita', 'imobiliaria')
    
    # CORREÇÃO: Atualizado para buscar dentro da relação ManyToMany (imoveis) e pelo campo correto (titulo_anuncio)
    search_fields = ('cliente__nome', 'cliente__razao_social', 'imoveis__titulo_anuncio')
    list_filter = ('imobiliaria', 'data_visita')

    def get_imoveis(self, obj):
        # Retorna uma string com os imóveis separados por vírgula
        return ", ".join([str(i) for i in obj.imoveis.all()])
    get_imoveis.short_description = 'Imóveis'
    
@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_vencimento', 'concluida', 'oportunidade', 'responsavel')
    search_fields = ('titulo', 'descricao', 'oportunidade__titulo')
    list_filter = ('concluida', 'data_vencimento', 'responsavel')

@admin.register(FunilEtapa)
class FunilEtapaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ordem', 'probabilidade_fechamento', 'imobiliaria', 'ativa')
    list_filter = ('imobiliaria', 'ativa')
    ordering = ('imobiliaria', 'ordem')
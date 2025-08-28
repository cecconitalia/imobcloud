# C:\wamp64\www\imobcloud\app_publicacoes\admin.py

from django.contrib import admin
from .models import PublicacaoHistorico, PublicacaoSocial, PostAgendado

@admin.register(PublicacaoHistorico)
class PublicacaoHistoricoAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'rede_social', 'data_publicacao')
    list_filter = ('rede_social', 'data_publicacao')
    search_fields = ('imovel__titulo_anuncio', 'rede_social')
    readonly_fields = ('data_publicacao',)

@admin.register(PublicacaoSocial)
class PublicacaoSocialAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'plataforma', 'data_publicacao', 'sucesso')
    list_filter = ('plataforma', 'sucesso', 'data_publicacao')
    search_fields = ('imovel__titulo_anuncio', 'texto_gerado')
    readonly_fields = ('data_publicacao',)

@admin.register(PostAgendado)
class PostAgendadoAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'data_agendamento', 'status', 'agendado_por')
    list_filter = ('status', 'data_agendamento')
    search_fields = ('imovel__titulo_anuncio', 'texto')
    readonly_fields = ('data_criacao',)
from django.contrib import admin
from .models import Vistoria, Ambiente, ItemVistoria, VistoriaFoto

class AmbienteInline(admin.TabularInline):
    model = Ambiente
    extra = 0

class VistoriaFotoInline(admin.TabularInline):
    model = VistoriaFoto
    extra = 0

@admin.register(Vistoria)
class VistoriaAdmin(admin.ModelAdmin):
    # Campos atualizados conforme o novo models.py
    list_display = ('id', 'contrato', 'tipo', 'data_vistoria', 'realizado_por_nome', 'concluida')
    list_filter = ('tipo', 'concluida', 'data_vistoria', 'data_criacao')
    search_fields = ('contrato__id', 'realizado_por_nome', 'observacoes')
    inlines = [AmbienteInline]

@admin.register(Ambiente)
class AmbienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'vistoria', 'nome')
    search_fields = ('nome', 'vistoria__id')
    list_filter = ('vistoria__tipo',)

@admin.register(ItemVistoria)
class ItemVistoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'ambiente', 'item', 'estado')
    list_filter = ('estado',)
    search_fields = ('item', 'ambiente__nome')
    inlines = [VistoriaFotoInline]

@admin.register(VistoriaFoto)
class VistoriaFotoAdmin(admin.ModelAdmin):
    # Atualizado de 'uploaded_at' para 'data_upload' e 'foto' para 'imagem'
    list_display = ('id', 'item', 'data_upload')
    list_filter = ('data_upload',)
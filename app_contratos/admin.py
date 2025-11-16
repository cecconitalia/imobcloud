# Em app_contratos/admin.py

from django.contrib import admin
from .models import Contrato, Pagamento, ModeloContrato
from core.models import Imobiliaria
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from app_financeiro.models import FormaPagamento
from django.utils.safestring import mark_safe


class PagamentoInline(admin.TabularInline):
    model = Pagamento
    extra = 0
    readonly_fields = ('data_pagamento', 'status')


@admin.register(ModeloContrato)
class ModeloContratoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'imobiliaria', 'tipo_contrato', 'padrao', 'data_atualizacao')
    list_filter = ('imobiliaria', 'tipo_contrato', 'padrao')
    search_fields = ('nome', 'imobiliaria__nome')
    
    # --- Início da Lista de Variáveis (HTML) ---
    VARIAVEIS_HELP_TEXT = """
    <div style="padding: 10px; margin-top: 15px; background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 4px; font-family: sans-serif; font-size: 0.9em; max-width: 800px;">
        <h4 style="margin-top:0;">Referência Rápida de Variáveis</h4>
        <p style="margin-top:0;">Use estas variáveis no campo "Conteúdo" acima. Elas serão substituídas pelos dados reais do contrato.</p>
        
        <h5 style="margin-bottom: 5px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">1. Dados Gerais</h5>
        <ul style="margin-top: 5px; padding-left: 20px;">
            <li><code>{{ data_hoje }}</code>: Data atual. (Formatar: <code>{{ data_hoje|date:"d \de F \de Y" }}</code>)</li>
        </ul>

        <h5 style="margin-bottom: 5px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">2. Dados do Contrato (<code>{{ contrato }}</code>)</h5>
        <ul style="margin-top: 5px; padding-left: 20px;">
            <li><code>{{ contrato.aluguel }}</code>: (Aluguel) Valor numérico do aluguel.</li>
            <li><code>{{ contrato.valor_total }}</code>: (Venda) Valor numérico total da venda.</li>
            <li><code>{{ contrato.duracao_meses }}</code>: (Aluguel) Duração em meses.</li>
            <li><code>{{ contrato.taxa_administracao_percentual }}</code>: (Aluguel) % da taxa de adm.</li>
            <li><code>{{ contrato.comissao_venda_percentual }}</code>: (Venda) % da comissão.</li>
            <li><code>{{ contrato.valor_comissao_acordado }}</code>: (Venda) Valor final em R$ da comissão.</li>
            <li><code>{{ contrato.data_inicio|date:"d/m/Y" }}</code>: Data de início.</li>
            <li><code>{{ contrato.data_fim|date:"d/m/Y" }}</code>: Data de término.</li>
            <li><code>{{ contrato.data_assinatura|date:"d/m/Y" }}</code>: Data de assinatura.</li>
            <li><code>{{ contrato.dia_vencimento }}</code>: (Aluguel) <strong>Apenas o dia</strong> do 1º vencimento (ex: 10).</li>
            <li><code>{{ contrato.data_vencimento_venda|date:"d/m/Y" }}</code>: (Venda) Data venc. comissão.</li>
            <li><code>{{ aluguel_extenso }}</code>: Valor do aluguel por extenso.</li>
            <li><code>{{ valor_total_extenso }}</code>: Valor total da venda por extenso.</li>
            <li><code>{{ valor_comissao_extenso }}</code>: Valor da comissão por extenso.</li>
            <li><code>{{ contrato.informacoes_adicionais }}</code>: Texto do campo "Informações Adicionais".</li>
        </ul>

        <h5 style="margin-bottom: 5px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">3. Dados da Imobiliária (<code>{{ imobiliaria }}</code>)</h5>
        <ul style="margin-top: 5px; padding-left: 20px;">
            <li><code>{{ imobiliaria.nome }}</code></li>
            <li><code>{{ imobiliaria.creci }}</code></li>
            <li><code>{{ imobiliaria.cnpj }}</code></li>
            <li><code>{{ imobiliaria.email_contato }}</code></li>
            <li><code>{{ imobiliaria.telefone }}</code></li>
            <li><code>{{ imobiliaria.cidade }}</code>, <code>{{ imobiliaria.uf }}</code></li>
        </ul>

        <h5 style="margin-bottom: 5px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">4. Dados do Imóvel (<code>{{ imovel }}</code>)</h5>
        <ul style="margin-top: 5px; padding-left: 20px;">
            <li><code>{{ imovel.titulo_anuncio }}</code></li>
            <li><code>{{ imovel.descricao_curta }}</code></li>
            <li><code>{{ imovel.logradouro }}</code>, <code>{{ imovel.numero }}</code>, <code>{{ imovel.bairro }}</code></li>
            <li><code>{{ imovel.cidade }}</code> - <code>{{ imovel.uf }}</code> (CEP: <code>{{ imovel.cep }}</code>)</li>
        </ul>

        <h5 style="margin-bottom: 5px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">5. Partes (Proprietário/Vendedor)</h5>
        <ul style="margin-top: 5px; padding-left: 20px;">
            <li><code>{% if locador_pf %}</code> (Verifica se é PF)</li>
            <li><code>{{ locador_pf.nome }}</code>, <code>{{ locador_pf.nacionalidade }}</code>, <code>{{ locador_pf.profissao }}</code>, <code>{{ locador_pf.rg }}</code></li>
            <li><code>{% elif locador_pj %}</code> (Verifica se é PJ)</li>
            <li><code>{{ locador_pj.razao_social }}</code></li>
            <li><code>{% endif %}</code></li>
            <li><code>{{ proprietario.documento }}</code> (CPF/CNPJ), <code>{{ proprietario.logradouro }}</code> (Endereço)</li>
        </ul>

        <h5 style="margin-bottom: 5px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">6. Partes (Inquilino/Comprador)</h5>
        <ul style="margin-top: 5px; padding-left: 20px;">
            <li><code>{% if locatario_pf %}</code> (Verifica se é PF)</li>
            <li><code>{{ locatario_pf.nome }}</code>, <code>{{ locatario_pf.nacionalidade }}</code>, <code>{{ locatario_pf.profissao }}</code>, <code>{{ locatario_pf.rg }}</code></li>
            <li><code>{% elif locatario_pj %}</code> (Verifica se é PJ)</li>
            <li><code>{{ locatario_pj.razao_social }}</code></li>
            <li><code>{% endif %}</code></li>
            <li><code>{{ inquilino.documento }}</code> (CPF/CNPJ), <code>{{ inquilino.logradouro }}</code> (Endereço)</li>
        </ul>

        <h5 style="margin-bottom: 5px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">7. Fiadores (Loop)</h5>
        <ul style="margin-top: 5px; padding-left: 20px;">
            <li><code>{% if fiadores_list %}</code> (Verifica se existem fiadores)</li>
            <li><code>{% for item in fiadores_list %}</code> (Inicia o loop)</li>
            <li><code>{{ item.pf.nome }}</code> (Nome se for PF)</li>
            <li><code>{{ item.pj.razao_social }}</code> (Razão Social se for PJ)</li>
            <li><code>{{ item.cliente.documento }}</code> (Documento do fiador)</li>
            <li><code>{% endfor %}</code> (Termina o loop)</li>
            <li><code>{% endif %}</code></li>
        </ul>
    </div>
    """
    # --- Fim da Lista de Variáveis ---
    
    def get_variaveis_display(self, obj=None):
        return mark_safe(self.VARIAVEIS_HELP_TEXT)
    get_variaveis_display.short_description = "" 

    readonly_fields = ('get_variaveis_display',)

    fieldsets = (
        (None, {
            'fields': ('imobiliaria', 'nome', 'tipo_contrato', 'padrao'),
        }),
        ('Conteúdo do Modelo', {
            'classes': ('collapse',), 
            'fields': (
                'conteudo', 
                'get_variaveis_display', 
            ),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'perfil') and request.user.perfil:
            return qs.filter(imobiliaria=request.user.perfil.imobiliaria)
        return qs.none() 

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "imobiliaria":
            if not request.user.is_superuser and hasattr(request.user, 'perfil') and request.user.perfil:
                kwargs["queryset"] = Imobiliaria.objects.filter(pk=request.user.perfil.imobiliaria.pk)
                kwargs["initial"] = request.user.perfil.imobiliaria
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not hasattr(obj, 'imobiliaria') or not obj.imobiliaria:
            if not request.user.is_superuser and hasattr(request.user, 'perfil') and request.user.perfil:
                obj.imobiliaria = request.user.perfil.imobiliaria
        super().save_model(request, obj, form, change)


@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    # ==========================================================
    # === ATUALIZAÇÃO: Admin de Contrato (Soft Delete)       ===
    # ==========================================================
    list_display = ('imovel', 'tipo_contrato', 'status_contrato', 'inquilino', 'proprietario', 'excluido') # <-- Adicionado 'excluido'
    list_filter = ('tipo_contrato', 'status_contrato', 'imobiliaria', 'excluido') # <-- Adicionado 'excluido'
    search_fields = ('imovel__titulo_anuncio', 'inquilino__nome', 'proprietario__nome')
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('imobiliaria', 'tipo_contrato', 'status_contrato', 'imovel', 'modelo_utilizado', 'excluido')
        }),
        ('Partes Envolvidas', {
            'fields': ('inquilino', 'proprietario', 'fiadores') 
        }),
        ('Valores e Prazos', {
            'fields': ('valor_total', 'duracao_meses', 'aluguel', 'data_inicio', 'data_fim', 'data_assinatura')
        }),
        ('Informações de Pagamento', {
            'fields': ('formas_pagamento',) 
        }),
        ('Conteúdo Personalizado', {
            'fields': ('conteudo_personalizado', 'informacoes_adicionais',)
        }),
    )
    
    inlines = [PagamentoInline]
    actions = ['marcar_como_excluido', 'recuperar_contrato']

    def get_queryset(self, request):
        # O Admin deve mostrar TODOS, incluindo os excluídos
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'perfil') and request.user.perfil:
            return qs.filter(imobiliaria=request.user.perfil.imobiliaria)
        return qs.none()
        
    @admin.action(description='Excluir contratos selecionados (Soft Delete)')
    def marcar_como_excluido(self, request, queryset):
        queryset.update(excluido=True)

    @admin.action(description='Recuperar contratos selecionados (Restaurar)')
    def recuperar_contrato(self, request, queryset):
        queryset.update(excluido=False)
    # ==========================================================

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and hasattr(request.user, 'perfil') and request.user.perfil:
            imobiliaria = request.user.perfil.imobiliaria
            
            if db_field.name == "imobiliaria":
                kwargs["queryset"] = Imobiliaria.objects.filter(pk=imobiliaria.pk)
                kwargs["initial"] = imobiliaria
            if db_field.name == "imovel":
                kwargs["queryset"] = Imovel.objects.filter(imobiliaria=imobiliaria)
            if db_field.name == "inquilino" or db_field.name == "proprietario":
                kwargs["queryset"] = Cliente.objects.filter(imobiliaria=imobiliaria)
            if db_field.name == "modelo_utilizado":
                obj_id = request.resolver_match.kwargs.get('object_id')
                tipo_contrato = None
                if obj_id:
                    try:
                        contrato = Contrato.objects.get(pk=obj_id)
                        tipo_contrato = contrato.tipo_contrato
                    except Contrato.DoesNotExist:
                        pass
                
                qs = ModeloContrato.objects.filter(imobiliaria=imobiliaria)
                if tipo_contrato:
                    qs = qs.filter(tipo_contrato=tipo_contrato)
                kwargs["queryset"] = qs

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if not request.user.is_superuser and hasattr(request.user, 'perfil') and request.user.perfil:
            imobiliaria = request.user.perfil.imobiliaria
            
            if db_field.name == "fiadores":
                kwargs["queryset"] = Cliente.objects.filter(imobiliaria=imobiliaria)
            if db_field.name == "formas_pagamento":
                kwargs["queryset"] = FormaPagamento.objects.filter(imobiliaria=imobiliaria)
        
        return super().formfield_for_manytomany(db_field, request, **kwargs)

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('contrato', 'valor', 'data_vencimento', 'data_pagamento', 'status')
    list_filter = ('status', 'data_vencimento')
    search_fields = ('contrato__imovel__titulo_anuncio',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'perfil') and request.user.perfil:
            return qs.filter(contrato__imobiliaria=request.user.perfil.imobiliaria)
        return qs.none()
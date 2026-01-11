# core/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Imobiliaria, PerfilUsuario, Notificacao, Plano, ConfiguracaoGlobal

# --- NOVA CONFIGURAÇÃO GLOBAL (Substitui .env) ---
@admin.register(ConfiguracaoGlobal)
class ConfiguracaoGlobalAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'site_url', 'modo_manutencao')
    
    fieldsets = (
        ('Geral', {
            'fields': ('site_url', 'base_public_url', 'modo_manutencao')
        }),
        ('Configurações de E-mail (SMTP)', {
            'fields': ('email_host', 'email_port', 'email_host_user', 'email_host_password', 'default_from_email'),
            'description': 'Credenciais para envio de e-mails do sistema.'
        }),
        ('Integrações e APIs', {
            'fields': ('google_api_key', 'cloudinary_cloud_name', 'cloudinary_api_key', 'cloudinary_api_secret')
        }),
    )

    def has_add_permission(self, request):
        # Impede criar mais de uma configuração (Singleton)
        # Se já existe 1 registro, não deixa adicionar outro.
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Evita deletar a configuração global acidentalmente
        return False

# --- ADMINISTRAÇÃO DE PLANOS ---
@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor', 'dias_ciclo', 'dias_para_bloqueio', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome',)

# --- ADMINISTRAÇÃO DE IMOBILIÁRIAS (COM FINANCEIRO) ---
class PerfilUsuarioInline(admin.TabularInline):
    model = PerfilUsuario
    extra = 0
    fields = ('username', 'email', 'is_admin', 'is_corretor')
    readonly_fields = ('username',)

@admin.register(Imobiliaria)
class ImobiliariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'subdominio', 'plano_contratado', 'status_financeiro', 'data_vencimento_atual', 'data_cadastro')
    list_filter = ('status_financeiro', 'plano_contratado', 'data_cadastro')
    search_fields = ('nome', 'subdominio', 'cnpj', 'email_contato')
    inlines = [PerfilUsuarioInline]
    
    fieldsets = (
        ('Dados Cadastrais', {
            'fields': ('nome', 'subdominio', 'cnpj', 'creci', 'email_contato', 'telefone')
        }),
        ('Financeiro (SaaS)', {
            'fields': ('plano_contratado', 'status_financeiro', 'data_vencimento_atual'),
            'description': 'Configure aqui o plano e o vencimento para controle automático de bloqueio.'
        }),
        ('Integrações Sociais', {
            'fields': ('facebook_page_id', 'instagram_business_account_id', 'facebook_user_access_token', 'facebook_page_access_token'),
            'classes': ('collapse',)
        }),
        ('Configurações IA e Estilo', {
            'fields': ('google_gemini_api_key', 'voz_da_marca_preferida', 'cor_primaria')
        }),
    )

    actions = ['atualizar_status_bloqueio']

    @admin.action(description='Forçar verificação de bloqueio/assinatura')
    def atualizar_status_bloqueio(self, request, queryset):
        count = 0
        for imob in queryset:
            imob.verificar_status_bloqueio()
            count += 1
        self.message_user(request, f"{count} imobiliárias verificadas com sucesso.")

# --- ADMINISTRAÇÃO DE USUÁRIOS ---
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'imobiliaria', 'is_admin', 'is_corretor', 'is_staff')
    list_filter = ('imobiliaria', 'is_admin', 'is_corretor', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'creci')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Profissionais', {'fields': ('imobiliaria', 'creci', 'is_admin', 'is_corretor')}),
        ('Endereço e Contato', {'fields': ('telefone', 'endereco_logradouro', 'endereco_numero', 'endereco_bairro', 'endereco_cidade', 'endereco_estado', 'endereco_cep')}),
        ('Integrações e Assinatura', {'fields': ('google_json_file', 'google_calendar_token', 'assinatura')}),
    )

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('destinatario', 'titulo', 'tipo', 'lida', 'data_criacao')
    list_filter = ('tipo', 'lida', 'data_criacao')
    search_fields = ('destinatario__username', 'mensagem')
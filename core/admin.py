import logging
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import Imobiliaria, PerfilUsuario, Notificacao
from django.contrib.auth.models import User as DjangoUser # Para desregistrar o User padrão

logger = logging.getLogger(__name__)

# Obtém o modelo de usuário customizado (core.PerfilUsuario)
User = get_user_model()

# Tentativa de desregistro seguro do User padrão do Django
try:
    admin.site.unregister(DjangoUser)
except admin.sites.NotRegistered:
    pass
except Exception:
    pass

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Campos customizados do PerfilUsuario integrados ao list_display
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'imobiliaria', 'is_admin', 'is_corretor')
    list_filter = ('is_staff', 'is_active', 'is_admin', 'is_corretor', 'imobiliaria')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'creci')
    ordering = ('username',)

    # Definimos a ordem dos campos no formulário de edição do usuário
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Informações Pessoais"), {"fields": ("first_name", "last_name", "email", 'telefone', 'creci', 'assinatura')}),
        (_("Permissões e Grupos"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "imobiliaria", 
                "is_admin",    
                "is_corretor", 
                "groups",
                "user_permissions",
            ),
        }),
        (_("Endereço e Observações"), {
            'fields': ('endereco_logradouro', 'endereco_numero', 'endereco_bairro', 'endereco_cidade', 'endereco_estado', 'endereco_cep', 'observacoes'),
            'classes': ('collapse',)
        }),
        (_("Integração Google"), {
            'fields': ('google_json_file', 'google_calendar_token'),
            'classes': ('collapse',)
        }),
        (_("Datas Importantes"), {"fields": ("last_login", "date_joined")}),
    )

@admin.register(Imobiliaria)
class ImobiliariaAdmin(admin.ModelAdmin):
    # 'telefone' e 'data_cadastro' agora existem
    list_display = ['nome', 'cnpj', 'creci', 'telefone', 'data_cadastro'] # 'telefone' adicionado aqui
    search_fields = ['nome', 'cnpj', 'telefone']
    readonly_fields = ['data_cadastro'] 
    
    fieldsets = (
        (None, {
            'fields': ('nome', 'cnpj', 'creci', 'data_cadastro', 'subdominio') # Adicionei subdominio
        }),
        ('Contatos', {
            'fields': ('telefone', 'email_contato', 'cor_primaria') # 'telefone' está aqui
        }),
        ('Integrações', {
            'fields': ('facebook_user_access_token', # 'facebook_user_access_token' está aqui
                       'facebook_page_access_token', 
                       'facebook_page_id', 
                       'instagram_business_account_id', # Adicionando o campo de instagram para consistência
                       'google_gemini_api_key', 
                       'voz_da_marca_preferida'),
            'description': 'Tokens e Chaves de API para uso da IA e redes sociais.',
        })
    )

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    # 'usuario' corrigido para 'destinatario'
    list_display = ('titulo', 'tipo', 'destinatario', 'lida', 'data_criacao') 
    list_filter = ('tipo', 'lida')
    search_fields = ('titulo', 'destinatario__username', 'destinatario__email') 
    readonly_fields = ('data_criacao',)
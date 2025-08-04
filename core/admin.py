# C:\wamp64\www\ImobCloud\core\admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Imobiliaria, PerfilUsuario

# Registra o modelo Imobiliaria no admin
@admin.register(Imobiliaria)
class ImobiliariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'subdominio', 'email_contato') # Adicionado email_contato para fácil visualização
    search_fields = ('nome', 'subdominio', 'email_contato')

# Inline para o PerfilUsuario ATUALIZADO
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil do Usuário'
    fk_name = 'user'
    # Adicionamos o campo 'cargo' para que apareça no admin do Utilizador
    fields = ('imobiliaria', 'cargo')

# Desregistra o admin padrão para User
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,) # O inline é o que adiciona os campos do perfil

    # Se você tem outras customizações como filter_horizontal ou list_filter, mantenha-as aqui.
    # filter_horizontal = BaseUserAdmin.filter_horizontal
    # list_filter = BaseUserAdmin.list_filter
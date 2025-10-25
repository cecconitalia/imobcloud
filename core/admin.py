# C:\wamp64\www\ImobCloud\core\admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Imobiliaria, PerfilUsuario

@admin.register(Imobiliaria)
class ImobiliariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'subdominio', 'email_contato')
    search_fields = ('nome', 'subdominio', 'email_contato')

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil do Usuário'
    fk_name = 'user'
    fields = ('imobiliaria', 'cargo', 'google_json_file')

admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)

# NOVO: Registra o modelo PerfilUsuario no admin
admin.site.register(PerfilUsuario)
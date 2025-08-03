# C:\wamp64\www\ImobCloud\core\admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Imobiliaria, PerfilUsuario

# Registra o modelo Imobiliaria no admin
@admin.register(Imobiliaria)
class ImobiliariaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'subdominio')
    search_fields = ('nome', 'subdominio')

# Inline para o PerfilUsuario
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'perfil'
    fk_name = 'user'

# Desregistra o admin padrão para User
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,) # O inline é o que adiciona o campo 'Imobiliaria'

    # REMOVA OU COMENTE ESTA SEÇÃO fieldsets QUE ESTAVA CAUSANDO O ERRO
    # fieldsets = BaseUserAdmin.fieldsets + (
    #     ('Informações da Imobiliária', {'fields': ('perfil__imobiliaria',)}),
    # )

    # Se você tem outras customizações como filter_horizontal ou list_filter, mantenha-as aqui.
    # filter_horizontal = BaseUserAdmin.filter_horizontal
    # list_filter = BaseUserAdmin.list_filter
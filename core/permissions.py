# C:\wamp64\www\ImobCloud\core\permissions.py

from rest_framework import permissions

class IsAdminOrSuperUser(permissions.BasePermission):
    """
    Permite acesso apenas a superusuários ou usuários com perfil de ADMIN.
    """
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
            
        # CORREÇÃO: Verifica o booleano is_admin em vez de cargo == 'ADMIN'
        if hasattr(request.user, 'perfil') and request.user.perfil.is_admin:
            return True
            
        return False

class IsCorretorOrReadOnly(permissions.BasePermission):
    """
    Permite acesso a corretores (para criar/editar) ou leitura para outros.
    Administradores também têm acesso total aqui.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        if request.user.is_superuser:
            return True
            
        # CORREÇÃO: Verifica se é Corretor OU Admin
        if hasattr(request.user, 'perfil'):
            return request.user.perfil.is_corretor or request.user.perfil.is_admin
            
        return False
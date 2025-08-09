# C:\wamp64\www\imobcloud\core\permissions.py

from rest_framework import permissions

class IsCorretorOrReadOnly(permissions.BasePermission):
    """
    Permite acesso de leitura para qualquer usuário autenticado.
    Permite acesso de escrita apenas para usuários com cargo de Corretor.
    """
    def has_permission(self, request, view):
        # Permite acesso de leitura para qualquer solicitação segura (GET, HEAD, OPTIONS).
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Permite acesso de escrita apenas para corretores.
        return request.user.is_authenticated and hasattr(request.user, 'perfil') and request.user.perfil.cargo == 'CORRETOR'
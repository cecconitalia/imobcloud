# C:\wamp64\www\imobcloud\core\permissions.py

from rest_framework import permissions
from core.models import PerfilUsuario # Importe o modelo para acessar as escolhas de cargo

class IsCorretorOrReadOnly(permissions.BasePermission):
    """
    Permite acesso de leitura para todos os usuários autenticados,
    mas exige o cargo 'CORRETOR' ou 'ADMIN' para operações de escrita.
    """
    def has_permission(self, request, view):
        # Permissões de leitura são permitidas para qualquer solicitação segura (GET, HEAD, OPTIONS).
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Permissões de escrita (POST, PUT, DELETE, etc.) são apenas para corretores ou administradores.
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'perfil') and
            (request.user.perfil.cargo == PerfilUsuario.Cargo.CORRETOR or request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN)
        )
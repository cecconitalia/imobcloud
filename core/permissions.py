# C:\wamp64\www\ImobCloud\core\permissions.py

from rest_framework import permissions
from rest_framework.request import Request
from typing import Any

class IsAdminOrSuperUser(permissions.BasePermission):
    """
    Permite acesso apenas a superusuários ou usuários com perfil de Administrador (is_admin=True).
    Utiliza o modelo PerfilUsuario (Custom User Model) do ImobCloud.
    Esta permissão corrige o erro de referência a '.perfil', acessando os atributos diretamente no User.
    """
    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        
        # Superusuários têm acesso irrestrito
        if user and user.is_superuser:
            return True
            
        # Verifica se o usuário está autenticado e possui a flag is_admin ativa.
        # No ImobCloud, PerfilUsuario herda de AbstractUser, portanto os campos booleanos
        # is_admin e is_corretor residem diretamente no objeto de usuário da requisição.
        if user and user.is_authenticated:
            return getattr(user, 'is_admin', False)
            
        return False

class IsCorretorOrReadOnly(permissions.BasePermission):
    """
    Permite acesso de escrita (POST, PUT, PATCH, DELETE) a corretores ou administradores.
    Permite leitura (GET, HEAD, OPTIONS) para qualquer usuário autenticado.
    Sincronizado com o modelo PerfilUsuario customizado.
    """
    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        
        # Bloqueio imediato de usuários não autenticados
        if not user or not user.is_authenticated:
            return False

        # Métodos de leitura (Safe Methods) são permitidos para qualquer membro autenticado
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Superusuários têm acesso de escrita irrestrito
        if user.is_superuser:
            return True
            
        # Verifica privilégios de Administrador ou Corretor no modelo PerfilUsuario
        is_admin: bool = getattr(user, 'is_admin', False)
        is_corretor: bool = getattr(user, 'is_corretor', False)
        
        return is_admin or is_corretor
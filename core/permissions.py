# core/permissions.py

from rest_framework import permissions
from rest_framework.request import Request
from typing import Any

class IsSubscriptionActive(permissions.BasePermission):
    """
    Bloqueia requisições se a imobiliária estiver com status BLOQUEADO ou CANCELADO.
    Define mensagens de erro específicas para o Frontend distinguir entre Teste e Assinatura.
    """
    message = "Acesso suspenso." # Mensagem padrão (fallback)

    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user

        # Superusuário do sistema (você) nunca é bloqueado
        if user and user.is_superuser:
            return True

        # Usuários não autenticados
        if not user or not user.is_authenticated:
            return True

        # Usuário sem imobiliária vinculada
        if not hasattr(user, 'imobiliaria') or not user.imobiliaria:
            return True

        # Verifica o status financeiro
        status = user.imobiliaria.status_financeiro
        
        # Se estiver bloqueado ou cancelado, nega o acesso
        if status in ['BLOQUEADO', 'CANCELADO']:
            # Lógica para definir a mensagem correta para o Frontend
            # Se não tem plano contratado (None), é porque estava no trial
            if not user.imobiliaria.plano_contratado:
                self.message = "TRIAL_EXPIRED"
            else:
                # Se tem plano, é inadimplência
                self.message = "SUBSCRIPTION_EXPIRED"
                
            return False
            
        return True

class IsAdminOrSuperUser(permissions.BasePermission):
    """
    Permite acesso apenas a superusuários ou usuários com perfil de Administrador (is_admin=True).
    Utiliza o modelo PerfilUsuario (Custom User Model) do ImobCloud.
    """
    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        
        if user and user.is_superuser:
            return True
            
        if user and user.is_authenticated:
            return getattr(user, 'is_admin', False)
            
        return False

class IsCorretorOrReadOnly(permissions.BasePermission):
    """
    Permite acesso de escrita a corretores ou administradores.
    Permite leitura para qualquer usuário autenticado.
    """
    def has_permission(self, request: Request, view: Any) -> bool:
        user = request.user
        
        if not user or not user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True
            
        if user.is_superuser:
            return True
            
        is_admin: bool = getattr(user, 'is_admin', False)
        is_corretor: bool = getattr(user, 'is_corretor', False)
        
        return is_admin or is_corretor
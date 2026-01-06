from django.utils.deprecation import MiddlewareMixin
from core.models import Imobiliaria
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings

User = get_user_model()

class TenantIdentificationMiddleware(MiddlewareMixin):
    """
    Middleware de Engenharia Sênior para isolamento multi-tenant.
    Responsável pela extração de Tenant via JWT, Sessão ou Subdomínio.
    Garante que toda requisição privada possua um request.tenant válido.
    """
    def process_request(self, request):
        host = request.get_host().split(':')[0]
        request.tenant = None
        
        # Identificadores de estado para depuração e auditoria
        user_info = f"User: {request.user.username}" if hasattr(request, 'user') and request.user.is_authenticated else "User: Anonymous"
        
        user = None
        # --- Fase 1: Autenticação JWT/Sessão ---
        # Verifica primeiro a sessão ativa (útil para Admin e visualização direta)
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        
        # Fallback para autenticação via Header Authorization (Padrão SPA/Mobile)
        elif 'HTTP_AUTHORIZATION' in request.META:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '').split(' ')
            if len(auth_header) == 2 and auth_header[0] == 'Bearer':
                token_str = auth_header[1]
                try:
                    # Utiliza-se a classe AccessToken do SimpleJWT para validação nativa.
                    token = AccessToken(token_str)
                    user_id = token[api_settings.USER_ID_CLAIM]
                    
                    if user_id:
                        user_from_token = User.objects.get(pk=user_id)
                        # Sincronização forçada para garantir que request.user esteja disponível em toda a stack
                        request.user = user_from_token
                        request._cached_user = user_from_token
                        user = user_from_token
                except (TokenError, User.DoesNotExist):
                    pass 

        # --- Fase 2: Identificação do Tenant ---
        if user and user.is_authenticated:
            if user.is_superuser:
                # Superusers podem personificar qualquer imobiliária via Header específico
                tenant_id = request.headers.get('X-Tenant-ID')
                if tenant_id:
                    try:
                        request.tenant = Imobiliaria.objects.get(id=int(tenant_id))
                    except (Imobiliaria.DoesNotExist, ValueError):
                        pass
            else:
                # Regra de Negócio: Usuários comuns devem obrigatoriamente ter uma imobiliária associada
                if hasattr(user, 'imobiliaria') and user.imobiliaria:
                    request.tenant = user.imobiliaria

        # --- Fase 3: Definição de Rotas Públicas ---
        public_paths = [
            '/',            # Libera a Home (Vue)
            '/favicon.ico', # Libera o ícone
            '/api/v1/public/',
            '/public/',
            '/admin/',
            '/media/',
            '/static/',     # Libera estáticos do Django
            '/assets/',     # Libera arquivos JS/CSS do Vue
            '/api/v1/token/',
            '/api/v1/token/refresh/',
            '/api/v1/core/login/',
            '/api/v1/core/refresh/',
            '/api/v1/core/register/',
            '/api/v1/relatorios/', 
            '/api/v1/core/public-register/' 
        ]

        # Verifica se o caminho atual é público
        is_public = request.path == '/' or any(request.path.startswith(p) for p in public_paths if p != '/')
        
        # Fallback de identificação por subdomínio
        if not request.tenant:
            subdomain = self._get_subdomain(host)
            
            # Ajuste crítico para reconhecimento do localhost no desenvolvimento
            if not subdomain and (host == 'localhost' or host == '127.0.0.1'):
                subdomain = 'localhost'
            
            if subdomain and subdomain not in ['www', 'api', 'admin']:
                try:
                    request.tenant = Imobiliaria.objects.get(subdominio=subdomain)
                except Imobiliaria.DoesNotExist:
                    pass

        # --- Fase 4: Validação de Segurança e Bloqueios ---
        
        # 1. Bloqueio de acesso anônimo em rotas privadas de API
        if not is_public and not (user and user.is_authenticated):
            # Se a requisição NÃO for para /api/ ou /admin/, deixa passar para o Vue (HTML)
            if not request.path.startswith('/api/') and not request.path.startswith('/admin/'):
                return None 
            
            return JsonResponse({"detail": "Autenticação necessária."}, status=403)

        # 2. Segurança Cross-Tenant
        if request.tenant and user and user.is_authenticated and not user.is_superuser:
            subdomain = self._get_subdomain(host)
            # Permite localhost ignorar validação de subdomínio para facilitar dev
            if subdomain and host != 'localhost' and subdomain not in ['www', 'api', 'admin', request.tenant.subdominio]:
                return HttpResponseForbidden("Acesso negado: Subdomínio incorreto para esta conta.")

        # 3. Bloqueio de API privada sem Tenant identificado
        if not is_public and not request.tenant and request.path.startswith('/api/'):
            return HttpResponseForbidden("Imobiliária não identificada.")

        return None

    def _get_subdomain(self, host: str) -> str:
        """Helper para extração de subdomínio baseada no host."""
        if host == 'localhost' or host == '127.0.0.1':
            return 'localhost'
            
        parts = host.split('.')
        # tenant1.localhost
        if parts[-1] == 'localhost':
            return parts[0] if len(parts) > 1 else 'localhost'
            
        # imobcloud.com
        if len(parts) > 2:
            return parts[0]
            
        return None
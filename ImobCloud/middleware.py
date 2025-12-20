# C:\wamp64\www\ImobCloud\ImobCloud\middleware.py

from django.utils.deprecation import MiddlewareMixin
from core.models import Imobiliaria
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.settings import api_settings
import jwt

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
        
        # Identificadores de estado para depuração
        user_info = f"User: {request.user.username}" if hasattr(request, 'user') and request.user.is_authenticated else "User: Anonymous"
        print(f"\nDEBUG MW Start: {user_info}, Host: {host}, Path: {request.path}")

        user = None
        # --- Fase 1: Autenticação JWT/Sessão ---
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            print(f"DEBUG MW Auth: Sessão ativa para '{user.username}'.")
        elif 'HTTP_AUTHORIZATION' in request.META:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '').split(' ')
            if len(auth_header) == 2 and auth_header[0] == 'Bearer':
                token = auth_header[1]
                try:
                    decoded_token = jwt.decode(token, api_settings.SIGNING_KEY, algorithms=[api_settings.ALGORITHM])
                    user_id = decoded_token.get(api_settings.USER_ID_CLAIM)
                    if user_id:
                        user_from_token = User.objects.get(pk=user_id)
                        # Sincronização forçada para compatibilidade com DRF
                        request.user = user_from_token
                        request._cached_user = user_from_token
                        user = user_from_token
                        print(f"DEBUG MW Auth: JWT válido para '{user.username}'.")
                except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
                    print(f"AVISO MW Auth: Falha na validação do token JWT.")

        # --- Fase 2: Identificação do Tenant ---
        if user and user.is_authenticated:
            if user.is_superuser:
                print("DEBUG MW Tenant: Superuser detectado.")
                tenant_id = request.headers.get('X-Tenant-ID')
                if tenant_id:
                    try:
                        request.tenant = Imobiliaria.objects.get(id=int(tenant_id))
                        print(f"DEBUG MW Tenant: Personificando {request.tenant.nome}")
                    except (Imobiliaria.DoesNotExist, ValueError):
                        print(f"AVISO MW Tenant: Tenant ID {tenant_id} inválido.")
            else:
                # Regra de negócio: Usuário comum deve estar vinculado a uma imobiliária
                if hasattr(user, 'imobiliaria') and user.imobiliaria:
                    request.tenant = user.imobiliaria
                    print(f"DEBUG MW Tenant: Identificado via Perfil ({request.tenant.nome})")
                else:
                    print(f"ERRO MW Tenant: Usuário '{user.username}' sem imobiliária associada.")

        # --- Fase 3: Regras de Acesso e Paths Públicos ---
        public_paths = [
            '/api/v1/public/',
            '/public/',
            '/admin/',
            '/media/',
            '/api/v1/token/',
            '/api/v1/token/refresh/',
            '/api/v1/core/login/',
            '/api/v1/core/refresh/',
            '/api/v1/core/register/',
            '/api/v1/relatorios/', # Aberto no middleware para validação de ACL na View
        ]

        is_public = any(request.path.startswith(p) for p in public_paths)
        
        # Se o path não é público e não temos usuário autenticado, bloqueamos imediatamente
        if not is_public and not (user and user.is_authenticated):
            print(f"BLOQUEIO MW: Acesso anônimo negado para {request.path}")
            return HttpResponseForbidden("Autenticação necessária.")

        # Validação de Subdomínio (Segurança Extra contra Session Hijacking)
        if request.tenant and not user.is_superuser:
            subdomain = self._get_subdomain(host)
            if subdomain and subdomain not in ['www', request.tenant.subdominio]:
                print(f"BLOQUEIO MW: Conflito de subdomínio '{subdomain}' vs '{request.tenant.subdominio}'")
                return HttpResponseForbidden("Acesso negado: Subdomínio incorreto para esta conta.")

        # Fallback de identificação por subdomínio (para acessos públicos que dependem de contexto)
        if not request.tenant:
            subdomain = self._get_subdomain(host)
            if not subdomain and (host == 'localhost' or host == '127.0.0.1'):
                subdomain = request.GET.get('subdomain')
            
            if subdomain and subdomain != 'www':
                try:
                    request.tenant = Imobiliaria.objects.get(subdominio=subdomain)
                    print(f"DEBUG MW Tenant: Identificado via Subdomínio ({request.tenant.nome})")
                except Imobiliaria.DoesNotExist:
                    print(f"AVISO MW Tenant: Subdomínio '{subdomain}' não existe.")

        if not is_public and not request.tenant:
            print(f"BLOQUEIO MW: Tenant não identificado para rota privada {request.path}")
            return HttpResponseForbidden("Imobiliária não identificada.")

        print(f"DEBUG MW Final: Permissão concedida para {request.path}. Tenant: {request.tenant.nome if request.tenant else 'Global'}")
        return None

    def _get_subdomain(self, host: str) -> str:
        """Helper para extração de subdomínio baseada no host."""
        parts = host.split('.')
        if parts[-1] == 'localhost':
            return parts[0] if len(parts) > 1 else None
        if parts[-2:] == ['imobcloud', 'com']:
            return parts[0] if len(parts) > 2 else None
        return None
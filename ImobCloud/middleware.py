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
        print(f"\nDEBUG MW Start: {user_info}, Host: {host}, Path: {request.path}")

        user = None
        # --- Fase 1: Autenticação JWT/Sessão ---
        # Verifica primeiro a sessão ativa (útil para Admin e visualização direta)
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            print(f"DEBUG MW Auth: Sessão ativa para '{user.username}'.")
        
        # Fallback para autenticação via Header Authorization (Padrão SPA/Mobile)
        elif 'HTTP_AUTHORIZATION' in request.META:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '').split(' ')
            if len(auth_header) == 2 and auth_header[0] == 'Bearer':
                token_str = auth_header[1]
                try:
                    # CORREÇÃO: Utiliza-se a classe AccessToken do SimpleJWT para validação nativa.
                    # Isso resolve falhas de validação manual por incompatibilidade de chaves ou algoritmos.
                    token = AccessToken(token_str)
                    user_id = token[api_settings.USER_ID_CLAIM]
                    
                    if user_id:
                        user_from_token = User.objects.get(pk=user_id)
                        # Sincronização forçada para garantir que request.user esteja disponível em toda a stack (DRF/ACLs)
                        request.user = user_from_token
                        request._cached_user = user_from_token
                        user = user_from_token
                        print(f"DEBUG MW Auth: JWT válido para '{user.username}'.")
                except (TokenError, User.DoesNotExist) as e:
                    # Captura erros de assinatura, expiração ou usuário inexistente
                    print(f"AVISO MW Auth: Falha na validação do token JWT: {str(e)}")

        # --- Fase 2: Identificação do Tenant ---
        if user and user.is_authenticated:
            if user.is_superuser:
                print("DEBUG MW Tenant: Superuser detectado.")
                # Superusers podem personificar qualquer imobiliária via Header específico
                tenant_id = request.headers.get('X-Tenant-ID')
                if tenant_id:
                    try:
                        request.tenant = Imobiliaria.objects.get(id=int(tenant_id))
                        print(f"DEBUG MW Tenant: Personificando {request.tenant.nome}")
                    except (Imobiliaria.DoesNotExist, ValueError):
                        print(f"AVISO MW Tenant: Tenant ID {tenant_id} inválido.")
            else:
                # Regra de Negócio: Usuários comuns devem obrigatoriamente ter uma imobiliária associada
                if hasattr(user, 'imobiliaria') and user.imobiliaria:
                    request.tenant = user.imobiliaria
                    print(f"DEBUG MW Tenant: Identificado via Perfil ({request.tenant.nome})")
                else:
                    print(f"ERRO MW Tenant: Usuário '{user.username}' em estado inconsistente (sem imobiliária).")

        # --- Fase 3: Definição de Rotas Públicas ---
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
            '/api/v1/relatorios/', # Validação de ACL delegada à camada de View
            '/api/v1/core/public-register/' # Cadastro
        ]

        is_public = any(request.path.startswith(p) for p in public_paths)
        
        # Fallback de identificação por subdomínio (essencial para landing pages e contextos anônimos)
        if not request.tenant:
            subdomain = self._get_subdomain(host)
            # Suporte para desenvolvimento local via query parameter se o subdomínio não for detectado no host
            if not subdomain and (host == 'localhost' or host == '127.0.0.1'):
                subdomain = request.GET.get('subdomain')
            
            if subdomain and subdomain not in ['www', 'api', 'admin']:
                try:
                    request.tenant = Imobiliaria.objects.get(subdominio=subdomain)
                    print(f"DEBUG MW Tenant: Identificado via Subdomínio ({request.tenant.nome})")
                except Imobiliaria.DoesNotExist:
                    print(f"AVISO MW Tenant: Subdomínio '{subdomain}' não existe.")

        # --- Fase 4: Validação de Segurança e Bloqueios ---
        
        # 1. Bloqueio de acesso anônimo em rotas privadas
        if not is_public and not (user and user.is_authenticated):
            print(f"BLOQUEIO MW: Acesso anônimo negado para {request.path}")
            return JsonResponse({"detail": "Autenticação necessária."}, status=403)

        # 2. Segurança Cross-Tenant (Anti-Session Hijacking)
        # Garante que um usuário autenticado não acesse dados de outro tenant via subdomínio incorreto
        if request.tenant and user and user.is_authenticated and not user.is_superuser:
            subdomain = self._get_subdomain(host)
            if subdomain and subdomain not in ['www', 'api', 'admin', request.tenant.subdominio]:
                print(f"BLOQUEIO MW: Conflito de subdomínio '{subdomain}' vs '{request.tenant.subdominio}'")
                return HttpResponseForbidden("Acesso negado: Subdomínio incorreto para esta conta.")

        # 3. Bloqueio de rota privada sem contexto de Tenant identificado
        if not is_public and not request.tenant:
            print(f"BLOQUEIO MW: Tenant não identificado para rota privada {request.path}")
            return HttpResponseForbidden("Imobiliária não identificada.")

        print(f"DEBUG MW Final: Permissão concedida para {request.path}. Tenant: {request.tenant.nome if request.tenant else 'Global'}")
        return None

    def _get_subdomain(self, host: str) -> str:
        """Helper para extração de subdomínio baseada no host."""
        parts = host.split('.')
        # Suporte para subdomínios em localhost (ex: tenant1.localhost)
        if parts[-1] == 'localhost':
            return parts[0] if len(parts) > 1 else None
        # Suporte para o domínio principal imobcloud.com
        if len(parts) > 2 and parts[-2] == 'imobcloud' and parts[-1] == 'com':
            return parts[0]
        # Suporte genérico para domínios de terceiros (ex: imob.exemplo.com.br)
        if len(parts) > 2:
            return parts[0]
        return None
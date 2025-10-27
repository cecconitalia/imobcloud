# C:\wamp64\www\ImobCloud\ImobCloud\middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import get_object_or_404, redirect 
from core.models import Imobiliaria, PerfilUsuario 
from django.http import HttpResponseNotFound, HttpResponseForbidden 
from django.contrib.auth import get_user_model 
from rest_framework_simplejwt.settings import api_settings 
import jwt 

User = get_user_model() 

class TenantIdentificationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().split(':')[0]
        request.tenant = None 
        
        user_info = f"User: {request.user.username}" if hasattr(request, 'user') and request.user.is_authenticated else "User: Anonymous"
        auth_info = f"Auth: {request.user.is_authenticated}" if hasattr(request, 'user') else "Auth: False"
        super_info = f"Super: {request.user.is_superuser}" if hasattr(request, 'user') else "Super: False"
        print(f"\nDEBUG MW Start: {user_info}, {auth_info}, {super_info}, Host: {host}, Path: {request.path}")

        identified_by_user_or_jwt = False 
        user_identified_tenant = None 
        is_superuser = False

        # --- Bloco de Autenticação (Sessão ou JWT) ---
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            print(f"DEBUG MW User: Usuário '{user.username}' identificado via Sessão Django.")
        
        elif 'HTTP_AUTHORIZATION' in request.META:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '').split(' ')
            if len(auth_header) == 2 and auth_header[0] == 'Bearer':
                token = auth_header[1]
                try:
                    decoded_token = jwt.decode(token, api_settings.SIGNING_KEY, algorithms=[api_settings.ALGORITHM])
                    user_id = decoded_token.get(api_settings.USER_ID_CLAIM)
                    if user_id:
                        user_from_token = User.objects.get(pk=user_id)
                        request._cached_user = user_from_token 
                        request.user = user_from_token 
                        user = user_from_token
                        print(f"DEBUG MW JWT: Usuário '{user.username}' identificado via JWT.")
                except jwt.ExpiredSignatureError:
                    print("AVISO: Token JWT expirado.")
                except (jwt.DecodeError, User.DoesNotExist):
                    print("AVISO: Token JWT inválido ou usuário não existe.")
                except Exception as e:
                    print(f"ERRO ao processar token JWT: {e}.")
        
        # --- Bloco de Definição de Tenant (APÓS autenticar) ---
        if user:
            identified_by_user_or_jwt = True
            if user.is_superuser:
                is_superuser = True
                print(f"DEBUG MW Tenant: Superuser identificado.")
                tenant_id_header = request.headers.get('X-Tenant-ID') 
                
                if tenant_id_header:
                    try:
                        tenant_personificado = Imobiliaria.objects.get(id=int(tenant_id_header))
                        request.tenant = tenant_personificado 
                        print(f"DEBUG MW Superuser: Personificando Tenant ID: {tenant_id_header} ({tenant_personificado.nome})")
                    except Imobiliaria.DoesNotExist:
                        print(f"AVISO MW Superuser: 'X-Tenant-ID' {tenant_id_header} não encontrado. Tenant remains None.")
                    except (ValueError, TypeError):
                        print(f"AVISO MW Superuser: 'X-Tenant-ID' ({tenant_id_header}) formato inválido. Tenant remains None.")
                else:
                    print(f"DEBUG MW Superuser: Nenhum header 'X-Tenant-ID' enviado. Tenant remains None.")
            else: # Usuário Comum
                try:
                    perfil = user.perfil 
                    if perfil.imobiliaria:
                        user_identified_tenant = perfil.imobiliaria
                        request.tenant = user_identified_tenant 
                        print(f"DEBUG MW Tenant: Usuário normal. Tenant: {user_identified_tenant.nome}")
                    else:
                        print(f"AVISO: Usuário '{user.username}' logado, mas sem imobiliária no perfil.")
                except PerfilUsuario.DoesNotExist:
                    print(f"AVISO: Usuário '{user.username}' logado, mas sem PerfilUsuario associado.")
                except Exception as e:
                    print(f"ERRO ao carregar imobiliária do perfil do usuário: {e}.")

        print(f"DEBUG MW Path: After User/JWT check. Current Tenant: {request.tenant.nome if request.tenant else 'None'}. User status: {'Authenticated' if user else 'Anonymous'}.")

        # --- CORREÇÃO: LÓGICA DE SAÍDA (EARLY EXIT) ---

        public_paths = [
            '/api/v1/public/',
            '/public/', # <<< CAMINHO PÚBLICO CORRETO ADICIONADO PARA EVITAR 403
            '/admin/',
            '/media/', 
            
            # Rotas do Simple JWT 
            '/api/v1/token/', 
            '/api/v1/token/refresh/',
            
            # Rotas do app 'core'
            '/api/v1/core/login/', 
            '/api/v1/core/refresh/',
            '/api/v1/core/register/',
        ]

        is_public_path = any(request.path.startswith(p) for p in public_paths)
        if is_public_path:
            print(f"DEBUG MW Path: Path é PÚBLICO ou MÍDIA. Exiting early from middleware.")
            return None 

        # Se NÃO for público E NÃO for autenticado, bloqueia
        if not is_public_path and not identified_by_user_or_jwt:
            print(f"ERRO MW: Usuário anônimo tentando acessar path privado ({request.path}). Bloqueando.")
            return HttpResponseForbidden("Autenticação necessária.")

        # Se for Superuser, a view decide sobre o tenant (pode ser None)
        if is_superuser:
            print(f"DEBUG MW Final Check: Superuser. Deixando a view decidir sobre o tenant. Exiting early.")
            return None 

        # Se for usuário normal, verifica consistência de subdomínio (se aplicável)
        if user_identified_tenant: 
            host = request.get_host().split(':')[0]
            subdomain_from_host = None
            if '.' in host:
                parts = host.split('.')
                if parts[-1] == 'localhost': 
                    if len(parts) > 1: subdomain_from_host = parts[0]
                elif parts[-2:] == ['imobcloud', 'com']: 
                    if len(parts) > 2: subdomain_from_host = parts[0]
            
            if subdomain_from_host and subdomain_from_host != 'www' and subdomain_from_host != user_identified_tenant.subdominio:
                print(f"ALERTA: Usuário '{request.user.username}' (tenant '{user_identified_tenant.subdominio}') tentou acessar o subdomínio '{subdomain_from_host}'. BLOQUEANDO API.")
                if request.path.startswith('/api/'):
                    return HttpResponseForbidden("Acesso negado. O subdomínio não corresponde à sua imobiliária logada.")

            print(f"DEBUG MW Final Check: Tenant '{request.tenant.nome}' verificado para usuário normal. Exiting early.")
            return None
        
        # === Lógica de Fallback (Subdomínio/Query Param para Anônimos) ===
        
        print(f"DEBUG MW Path: Falling back to Subdomain/QueryParam logic for Anonymous user on non-public path.")
        
        subdomain = None 
        if '.' in host: 
            parts = host.split('.')
            if parts[-1] == 'localhost': 
                if len(parts) > 1: subdomain = parts[0]
            elif parts[-2:] == ['imobcloud', 'com']: 
                if len(parts) > 2: subdomain = parts[0]
            
        if subdomain and subdomain != 'www':
            try:
                tenant_by_subdomain = Imobiliaria.objects.get(subdominio=subdomain)
                request.tenant = tenant_by_subdomain
                print(f"DEBUG MW Subdomain Fallback: Tenant identified by subdomain: {request.tenant.nome}")
            except Imobiliaria.DoesNotExist:
                print(f"AVISO Fallback: Imobiliária com subdomínio '{subdomain}' não encontrada.")
            except Exception as e:
                print(f"ERRO Fallback (Subdomain): {e}.")

        if request.tenant is None and (host == 'localhost' or host == '127.0.0.1'):
             subdomain_param = request.GET.get('subdomain', None)
             if subdomain_param:
                 try:
                     tenant_by_param = Imobiliaria.objects.get(subdominio=subdomain_param)
                     request.tenant = tenant_by_param
                     print(f"DEBUG MW Fallback: Tenant identified by query param 'subdomain': {request.tenant.nome}")
                 except Imobiliaria.DoesNotExist:
                     print(f"AVISO Fallback: Imobiliária com subdomínio '{subdomain_param}' não encontrada via query param.")
                 except Exception as e:
                     print(f"ERRO Fallback (Query Param): {e}.")
             else:
                print("ERRO MW Fallback: Anônimo em path privado sem identificação de tenant. Bloqueando.")
                return HttpResponseForbidden("Acesso não autorizado ou imobiliária não identificada.") 

        if request.tenant:
             print(f"DEBUG MW End (Fallback): Final request.tenant: {request.tenant.nome}. Permitting.")
             return None
        else:
             print(f"ERRO MW End (Fallback): Nenhum tenant identificado. Bloqueando path {request.path}.")
             return HttpResponseForbidden("Imobiliária não identificada.")
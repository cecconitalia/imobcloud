# C:\wamp64\www\ImobCloud\ImobCloud\middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import get_object_or_404, redirect # Importar redirect
from core.models import Imobiliaria, PerfilUsuario 
from django.http import HttpResponseNotFound, HttpResponseForbidden # Importar HttpResponseForbidden
from django.contrib.auth import get_user_model 
from rest_framework_simplejwt.settings import api_settings 
import jwt 

User = get_user_model() 

class TenantIdentificationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().split(':')[0]
        request.tenant = None 
        
        # DEBUG: Log no início do middleware
        user_info = f"User: {request.user.username}" if hasattr(request, 'user') and request.user.is_authenticated else "User: Anonymous"
        auth_info = f"Auth: {request.user.is_authenticated}" if hasattr(request, 'user') else "Auth: False"
        super_info = f"Super: {request.user.is_superuser}" if hasattr(request, 'user') else "Super: False"
        print(f"\nDEBUG MW Start: {user_info}, {auth_info}, {super_info}, Host: {host}, Path: {request.path}")

        # === 1. Tenta identificar o tenant pelo USUÁRIO LOGADO (Pelo Django Auth ou decodificando JWT) ===
        identified_by_user_or_jwt = False 
        user_identified_tenant = None # Para guardar o tenant identificado pelo usuário
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
            
            # --- CORREÇÃO 1: LÓGICA DE PERSONIFICAÇÃO DE SUPERUSER ---
            if user.is_superuser:
                is_superuser = True
                print(f"DEBUG MW Tenant: Superuser identificado.")
                tenant_id_header = request.headers.get('X-Tenant-ID') # Padrão 'X-Tenant-ID'
                
                if tenant_id_header:
                    try:
                        # Tenta buscar o tenant pelo header
                        tenant_personificado = Imobiliaria.objects.get(id=int(tenant_id_header))
                        request.tenant = tenant_personificado # Define o tenant personificado
                        print(f"DEBUG MW Superuser: Personificando Tenant ID: {tenant_id_header} ({tenant_personificado.nome})")
                    except Imobiliaria.DoesNotExist:
                        print(f"AVISO MW Superuser: 'X-Tenant-ID' {tenant_id_header} não encontrado. Tenant remains None.")
                    except (ValueError, TypeError):
                        print(f"AVISO MW Superuser: 'X-Tenant-ID' ({tenant_id_header}) formato inválido. Tenant remains None.")
                else:
                    print(f"DEBUG MW Superuser: Nenhum header 'X-Tenant-ID' enviado. Tenant remains None.")

            # Se for usuário comum, apenas pegue a imobiliária dele
            else:
                try:
                    perfil = user.perfil 
                    if perfil.imobiliaria:
                        user_identified_tenant = perfil.imobiliaria
                        request.tenant = user_identified_tenant # Define o tenant do usuário
                        print(f"DEBUG MW Tenant: Usuário normal. Tenant: {user_identified_tenant.nome}")
                    else:
                        print(f"AVISO: Usuário '{user.username}' logado, mas sem imobiliária no perfil.")
                except PerfilUsuario.DoesNotExist:
                    print(f"AVISO: Usuário '{user.username}' logado, mas sem PerfilUsuario associado.")
                except Exception as e:
                    print(f"ERRO ao carregar imobiliária do perfil do usuário: {e}.")
            # --- FIM DA CORREÇÃO 1 ---

        print(f"DEBUG MW Path: After User/JWT check. Current Tenant: {request.tenant.nome if request.tenant else 'None'}. User status: {'Authenticated' if user else 'Anonymous'}.")

        # --- CORREÇÃO 2: LÓGICA DE SAÍDA (EARLY EXIT) ---

        # Lista de caminhos que são SEMPRE públicos (login, registro, etc)
        public_paths = [
            '/api/v1/public/',
            '/admin/',
            '/api/v1/token/', 
            '/api/v1/token/refresh/',
            '/api/v1/core/login/', 
            '/api/v1/core/refresh/',
            '/api/v1/core/register/',
        ]
        is_public_path = any(request.path.startswith(p) for p in public_paths)
        if is_public_path:
            print(f"DEBUG MW Path: Path é PÚBLICO. Exiting early from middleware.")
            return None # Continua para a view (pública)

        # Se NÃO for público E NÃO for autenticado, bloqueia
        if not is_public_path and not identified_by_user_or_jwt:
            print(f"ERRO MW: Usuário anônimo tentando acessar path privado. Bloqueando.")
            return HttpResponseForbidden("Autenticação necessária.")

        # Se for Superuser, a lógica de personificação (Correção 1) já tratou o tenant.
        # A view (views.py) vai decidir se `tenant=None` é aceitável ou não.
        if is_superuser:
            print(f"DEBUG MW Final Check: Superuser. Deixando a view decidir sobre o tenant. Exiting early.")
            return None # Continua para a view (ex: DashboardStatsView)

        # Se for usuário normal, verifica consistência de subdomínio
        if user_identified_tenant: # Se um tenant foi identificado pelo usuário logado
            subdomain_from_host = None
            if '.' in host:
                parts = host.split('.')
                if parts[-1] == 'localhost': 
                    if len(parts) > 1: subdomain_from_host = parts[0]
                elif parts[-2:] == ['imobcloud', 'com']: # Para produção
                    if len(parts) > 2: subdomain_from_host = parts[0]
            
            # Se o usuário está em um subdomínio E esse subdomínio não corresponde ao seu tenant
            if subdomain_from_host and subdomain_from_host != 'www' and subdomain_from_host != user_identified_tenant.subdominio:
                print(f"ALERTA: Usuário '{request.user.username}' (tenant '{user_identified_tenant.subdominio}') tentou acessar o subdomínio '{subdomain_from_host}'. BLOQUEANDO.")
                if request.path.startswith('/api/'):
                    return HttpResponseForbidden("Acesso negado. O subdomínio não corresponde à sua imobiliária logada.")
                else:
                    correct_url = f"http://{user_identified_tenant.subdominio}.localhost:5173{request.path}"
                    return redirect(correct_url)
            
            print(f"DEBUG MW Final Check: Tenant '{request.tenant.nome}' verificado. Exiting early.")
            return None # Sai aqui para usuários logados
        
        # --- FIM DA CORREÇÃO 2 ---

        # === 2. Se não há usuário logado/identificado, tenta identificar o tenant pelo SUBDOMÍNIO do HOSTNAME ===
        # (Esta lógica agora só roda para usuários ANÔNIMOS em paths NÃO PÚBLICOS (ex: site público de imobiliária))
        print(f"DEBUG MW Path: Falling back to Subdomain logic (Unauthenticated). Current Tenant: {request.tenant.nome if request.tenant else 'None'}")
        
        subdomain = None # Recalcula subdomain para este bloco
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
                print(f"DEBUG MW Subdomain: Tenant identified by subdomain (Unauthenticated): {request.tenant.nome}")
            except Imobiliaria.DoesNotExist:
                print(f"AVISO: Imobiliária com subdomínio '{subdomain}' não encontrada (Unauthenticated). Tenant remains None.")
            except Exception as e:
                print(f"ERRO ao carregar imobiliária por subdomínio (Unauthenticated): {e}. Tenant remains None.")

        # 3. Fallback para desenvolvimento LOCALHOST (se nenhuma das anteriores funcionou)
        if request.tenant is None and (host == 'localhost' or host == '127.0.0.1'):
             subdomain_param = request.GET.get('subdomain', None)
             if subdomain_param:
                 try:
                     tenant_by_param = Imobiliaria.objects.get(subdominio=subdomain_param)
                     request.tenant = tenant_by_param
                     print(f"DEBUG MW Fallback: Tenant identified by query param 'subdomain' for public views: {request.tenant.nome}")
                 except Imobiliaria.DoesNotExist:
                     print(f"AVISO: Imobiliária com subdomínio '{subdomain_param}' não encontrada via query param. Tenant remains None.")
                 except Exception as e:
                     print(f"ERRO ao carregar imobiliária por query param: {e}. Tenant remains None.")
             else:
                print("AVISO: Nenhuma imobiliária padrão definida para localhost (fallback final). Site público geral será vazio.")

        # DEBUG: Log final do middleware (se não saiu antes)
        print(f"DEBUG MW End: Final request.tenant: {request.tenant.nome if request.tenant else 'None'} (No early return).")
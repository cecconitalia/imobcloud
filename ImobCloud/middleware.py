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

        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.is_superuser:
                request.tenant = None 
                print(f"DEBUG MW User: Superuser. Tenant set to None.")
            else:
                try:
                    perfil = request.user.perfil 
                    if perfil.imobiliaria:
                        user_identified_tenant = perfil.imobiliaria # Armazena o tenant do usuário
                        request.tenant = user_identified_tenant # Temporariamente define request.tenant
                        print(f"DEBUG MW User: Normal user '{request.user.username}'. Tenant from profile (Django Auth): {user_identified_tenant.nome}")
                    else:
                        print(f"AVISO: Usuário '{request.user.username}' logado, mas sem imobiliária associada em seu perfil. Tenant is None.")
                except PerfilUsuario.DoesNotExist:
                    print(f"AVISO: Usuário '{request.user.username}' logado, mas sem PerfilUsuario associado. Tenant is None.")
                except Exception as e:
                    print(f"ERRO ao carregar imobiliária do perfil do usuário (Django Auth): {e}. Tenant is None.")
            identified_by_user_or_jwt = True 

        if not identified_by_user_or_jwt and 'HTTP_AUTHORIZATION' in request.META:
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
                        
                        # *** CORREÇÃO ***
                        # Esta flag é essencial para pular a lógica de fallback anônima
                        identified_by_user_or_jwt = True 
                        
                        if user_from_token.is_superuser:
                            request.tenant = None 
                            print(f"DEBUG MW JWT: Superuser identificado por JWT. Tenant set to None.")
                        else:
                            perfil = user_from_token.perfil
                            if perfil.imobiliaria:
                                user_identified_tenant = perfil.imobiliaria # Armazena o tenant do usuário
                                request.tenant = user_identified_tenant # Temporariamente define request.tenant
                                print(f"DEBUG MW JWT: Usuário '{user_from_token.username}' identificado por JWT. Tenant: {user_identified_tenant.nome}")
                            else:
                                print(f"AVISO: Usuário '{user_from_token.username}' identificado por JWT, mas sem imobiliária no perfil.")
                    else:
                        print("AVISO: ID de usuário não encontrado no token JWT decodificado.")
                except jwt.ExpiredSignatureError:
                    print("AVISO: Token JWT expirado (decodificado manualmente).")
                except jwt.DecodeError:
                    print("AVISO: Erro de decodificação de token JWT (inválido).")
                except User.DoesNotExist:
                    print("AVISO: Usuário do token JWT não encontrado no BD.")
                except Exception as e:
                    print(f"ERRO ao processar token JWT manualmente: {e}. Token/User might be invalid.")
            
        # DEBUG: Log após TODA a tentativa de identificar pelo usuário/JWT
        print(f"DEBUG MW Path: After User/JWT check. Current Tenant: {request.tenant.nome if request.tenant else 'None'}. User status: {'Authenticated' if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'}.")


        # === NOVO: VERIFICAÇÃO DE CONSISTÊNCIA ENTRE USUÁRIO E SUBDOMÍNIO ===
        if user_identified_tenant: # Se um tenant foi identificado pelo usuário logado
            subdomain_from_host = None
            if '.' in host: # Analisa o hostname completo (ex: sol.localhost)
                parts = host.split('.')
                if parts[-1] == 'localhost': 
                    if len(parts) > 1:
                        subdomain_from_host = parts[0]
                elif parts[-2:] == ['imobcloud', 'com']: # Para produção
                    if len(parts) > 2:
                        subdomain_from_host = parts[0]
            
            # Se o usuário está em um subdomínio E esse subdomínio não corresponde ao seu tenant
            if subdomain_from_host and subdomain_from_host != 'www' and subdomain_from_host != user_identified_tenant.subdominio:
                print(f"ALERTA: Usuário '{request.user.username}' (tenant '{user_identified_tenant.subdominio}') tentou acessar o subdomínio '{subdomain_from_host}'. REDIRECIONANDO/BLOQUEANDO.")
                
                # Para APIs REST, retorne um 403 Forbidden ou 404 Not Found para não vazar informações
                # Para navegação de página, um redirect é melhor
                if request.path.startswith('/api/'): # Se for uma chamada de API
                    return HttpResponseForbidden("Acesso negado. O subdomínio não corresponde à sua imobiliária logada.")
                else: # Se for navegação de página, redirecione
                    # Construa a URL de redirecionamento para o subdomínio correto do usuário
                    correct_url = f"http://{user_identified_tenant.subdominio}.localhost:5173{request.path}"
                    return redirect(correct_url)
            
        # Se o usuário está logado e o subdomínio corresponde ou não há subdomínio,
        # OU se é superusuário, o middleware termina aqui.
        
        # Este bloco 'return' agora será alcançado corretamente por usuários JWT
        # porque 'identified_by_user_or_jwt' estará True.
        if identified_by_user_or_jwt:
            print(f"DEBUG MW Final Check: Tenant identified or Superuser. Tenant: {request.tenant.nome if request.tenant else 'None'}. Exiting early from middleware.")
            return # Sai aqui para usuários logados que acessam o subdomínio correto ou sem subdomínio


        # === 2. Se não há usuário logado/identificado, tenta identificar o tenant pelo SUBDOMÍNIO do HOSTNAME ===
        print(f"DEBUG MW Path: Falling back to Subdomain logic (Unauthenticated). Current Tenant: {request.tenant.nome if request.tenant else 'None'}")
        
        subdomain = None # Recalcula subdomain para este bloco
        if '.' in host: 
            parts = host.split('.')
            if parts[-1] == 'localhost': 
                if len(parts) > 1:
                    subdomain = parts[0]
            elif parts[-2:] == ['imobcloud', 'com']: 
                if len(parts) > 2:
                    subdomain = parts[0]
            
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
                     # AQUI ESTÁ A CORREÇÃO que você já havia feito: "subdomino" foi alterado para "subdominio"
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
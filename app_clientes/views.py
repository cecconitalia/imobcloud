# C:\wamp64\www\ImobCloud\app_clientes\views.py

import os
import json
import logging
import base64
from io import BytesIO
from datetime import date, timedelta

from django.conf import settings
from django.db import models  # Import necessário para Aggregations
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth, Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from django.contrib.staticfiles import finders

from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated

from google_auth_oauthlib.flow import Flow
from xhtml2pdf import pisa

from core.models import PerfilUsuario, Notificacao, Imobiliaria
from core.permissions import IsAdminOrSuperUser
from .models import Oportunidade, Tarefa, Cliente, Visita, Atividade, FunilEtapa
from .serializers import (
    OportunidadeSerializer,
    TarefaSerializer,
    ClienteSerializer,
    VisitaSerializer,
    AtividadeSerializer,
    FunilEtapaSerializer,
    UsuarioSimplesSerializer,
    ClienteSimplesSerializer
)
from ImobCloud.utils.google_calendar_api import agendar_tarefa_no_calendario
from app_imoveis.models import Imovel

User = get_user_model()
logger = logging.getLogger(__name__)

# ====================================================================
# HELPER: CONVERTER IMAGEM PARA BASE64
# ====================================================================
def image_to_base64(image_field):
    if not image_field or not hasattr(image_field, 'name') or not image_field.name:
        return None
    try:
        file_path = None
        if hasattr(image_field, 'path'):
            file_path = image_field.path
        elif hasattr(settings, 'MEDIA_ROOT'):
            file_path = os.path.join(settings.MEDIA_ROOT, image_field.name)

        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode('utf-8')
            ext = os.path.splitext(file_path)[1].lower().replace('.', '')
            if ext == 'jpg': ext = 'jpeg'
            if not ext: ext = 'png'
            return f"data:image/{ext};base64,{encoded_string}"
    except Exception as e:
        logger.error(f"Erro ao converter imagem para base64: {e}")
        return None
    return None

def is_admin_or_corretor(user):
    is_admin_bool = getattr(user, 'is_admin', False)
    is_corretor_bool = getattr(user, 'is_corretor', False)
    cargo = getattr(user, 'cargo', None)
    is_admin_cargo = (str(cargo).upper() == 'ADMIN')
    is_corretor_cargo = (str(cargo).upper() == 'CORRETOR')
    return is_admin_bool or is_corretor_bool or is_admin_cargo or is_corretor_cargo

# ====================================================================
# VIEWS DO GOOGLE CALENDAR
# ====================================================================
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_DIR = os.path.join(settings.MEDIA_ROOT, 'google_credentials')

class GoogleCalendarAuthView(APIView):
    authentication_classes = [] 
    permission_classes = [AllowAny] 

    def get(self, request, *args, **kwargs):
        try:
            user = None
            token = request.query_params.get('token')
            if token:
                try:
                    jwt_auth = JWTAuthentication()
                    validated_token = jwt_auth.get_validated_token(token)
                    user = jwt_auth.get_user(validated_token)
                except Exception as e:
                    pass
            
            if not user and request.user and request.user.is_authenticated:
                user = request.user

            if not user:
                return HttpResponse("Autenticação necessária. Token JWT inválido ou não fornecido na URL.", status=401)

            if not getattr(user, 'google_json_file', None):
                return HttpResponse(f"Erro: Usuário {user.username} não possui arquivo de credenciais do Google configurado.", status=400)
            
            json_file_path = default_storage.path(user.google_json_file.name)
            callback_url = request.build_absolute_uri(reverse('google-calendar-auth-callback'))
            
            if 'localhost' in callback_url or '127.0.0.1' in callback_url or 'http:' in callback_url:
                 os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

            flow = Flow.from_client_secrets_file(
                json_file_path,
                scopes=SCOPES,
                redirect_uri=callback_url
            )
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
    
            request.session['oauth_state'] = state
            request.session['auth_user_id'] = user.id
            request.session.modified = True
            
            return HttpResponseRedirect(authorization_url)
            
        except Exception as e:
            logger.error(f"Erro Auth Google: {e}")
            return HttpResponse(f"Erro interno: {str(e)}", status=400)

class GoogleCalendarAuthCallbackView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user_id = request.session.get('auth_user_id')
        state = request.session.get('oauth_state')
        
        if not user_id or not state:
            return HttpResponse("Sessão expirada. Por favor, volte ao sistema e tente conectar novamente.", status=400)
        
        if state != request.query_params.get('state'):
            return HttpResponse("Estado inválido (Erro de segurança). Tente novamente.", status=400)
        
        try:
            user = User.objects.get(id=user_id)
            if not getattr(user, 'google_json_file', None):
                 return HttpResponse("Erro: Arquivo de credenciais não encontrado.", status=400)

            json_file_path = default_storage.path(user.google_json_file.name)
            callback_url = request.build_absolute_uri(reverse('google-calendar-auth-callback'))
            if 'localhost' in callback_url or '127.0.0.1' in callback_url or 'http:' in callback_url:
                 os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

            flow = Flow.from_client_secrets_file(
                json_file_path,
                scopes=SCOPES,
                redirect_uri=callback_url
            )
            
            flow.fetch_token(authorization_response=request.get_full_path())
            
            credentials_json = {
                'token': flow.credentials.token,
                'refresh_token': flow.credentials.refresh_token,
                'token_uri': flow.credentials.token_uri,
                'client_id': flow.credentials.client_id,
                'client_secret': flow.credentials.client_secret,
                'scopes': flow.credentials.scopes
            }
            
            user.google_calendar_token = json.dumps(credentials_json)
            user.save()
            
            if 'oauth_state' in request.session: del request.session['oauth_state']
            if 'auth_user_id' in request.session: del request.session['auth_user_id']
            
            return HttpResponseRedirect("/integracoes?status=success_google")
            
        except User.DoesNotExist:
            return HttpResponse("Usuário não encontrado.", status=400)
        except Exception as e:
            logger.error(f"Erro Google Calendar Callback: {e}")
            return HttpResponse(f"Erro ao processar a conexão: {str(e)}", status=400)

# ====================================================================
# VIEWS DO CRM
# ====================================================================

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'documento', 'razao_social', 'email', 'telefone']
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        base_queryset = Cliente.objects.filter(ativo=True)
        user = self.request.user
        
        tenant = getattr(self.request, 'tenant', None)
        if not tenant and hasattr(user, 'imobiliaria'):
            tenant = user.imobiliaria

        if user.is_superuser:
            if not tenant:
                return base_queryset.all().order_by('-id')
            return base_queryset.filter(imobiliaria=tenant).order_by('-id')
        
        if tenant:
            return base_queryset.filter(imobiliaria=tenant).order_by('-id')
            
        return Cliente.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset() 
        
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(perfil_cliente__contains=[tipo])
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None)
        if not tenant and hasattr(self.request.user, 'imobiliaria'):
            tenant = self.request.user.imobiliaria

        if self.request.user.is_superuser:
            if 'imobiliaria' in self.request.data:
                imobiliaria_id = self.request.data['imobiliaria']
                imobiliaria_obj = get_object_or_404(Imobiliaria, pk=imobiliaria_id)
                serializer.save(imobiliaria=imobiliaria_obj)
            elif tenant:
                serializer.save(imobiliaria=tenant)
            else:
                first_tenant = Imobiliaria.objects.first()
                if first_tenant:
                    serializer.save(imobiliaria=first_tenant)
                else:
                    serializer.save() 
        else:
            if tenant:
                serializer.save(imobiliaria=tenant)
            else:
                raise PermissionDenied("Usuário sem imobiliária vinculada.")
            
    def perform_update(self, serializer):
        user = self.request.user
        tenant = getattr(self.request, 'tenant', None) or getattr(user, 'imobiliaria', None)

        if user.is_superuser:
            serializer.save()
        elif is_admin_or_corretor(user) and serializer.instance.imobiliaria == tenant:
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar este cliente.")

    def perform_destroy(self, instance):
        user = self.request.user
        tenant = getattr(self.request, 'tenant', None) or getattr(user, 'imobiliaria', None)

        if user.is_superuser or (is_admin_or_corretor(user) and instance.imobiliaria == tenant):
            instance.ativo = False
            instance.save()
        else:
            raise PermissionDenied("Você não tem permissão para inativar este cliente.")

    @action(detail=False, methods=['get'], url_path='lista-simples')
    def lista_simples(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = ClienteSimplesSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='lista-proprietarios')
    def lista_proprietarios(self, request):
        base_queryset = self.get_queryset()
        queryset = base_queryset.filter(
            perfil_cliente__contains=['PROPRIETARIO']
        ).distinct()
        serializer = ClienteSimplesSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def atividades(self, request, pk=None):
        cliente = self.get_object()
        atividades = cliente.atividades.all()
        serializer = AtividadeSerializer(atividades, many=True)
        return Response(serializer.data)


class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all()
    serializer_class = VisitaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        tenant = getattr(self.request, 'tenant', None) or getattr(user, 'imobiliaria', None)

        if user.is_superuser:
            if not tenant:
                return Visita.objects.all().prefetch_related('imoveis', 'cliente')
            return Visita.objects.filter(imobiliaria=tenant).prefetch_related('imoveis', 'cliente')
        
        if tenant:
            return Visita.objects.filter(imobiliaria=tenant).prefetch_related('imoveis', 'cliente')
        return Visita.objects.none()

    def perform_create(self, serializer):
        cliente_id = self.request.data.get('cliente')
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)
        imobiliaria = tenant

        if not imobiliaria and self.request.user.is_superuser:
            imoveis_data = self.request.data.get('imoveis')
            if imoveis_data and isinstance(imoveis_data, list) and len(imoveis_data) > 0:
                try:
                    primeiro_id = imoveis_data[0]
                    imovel_obj = Imovel.objects.get(pk=primeiro_id)
                    imobiliaria = imovel_obj.imobiliaria
                except (Imovel.DoesNotExist, IndexError, ValueError):
                    pass
            
            if not imobiliaria and cliente.imobiliaria:
                imobiliaria = cliente.imobiliaria
            
            if not imobiliaria:
                 imobiliaria = Imobiliaria.objects.first()
        
        if not imobiliaria:
            raise PermissionDenied("Não foi possível associar a visita. Tenant/Imobiliária não identificada.")

        serializer.save(imobiliaria=imobiliaria, cliente=cliente, corretor=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)
        
        if (instance.assinatura_cliente or instance.assinatura_corretor):
             dados = self.request.data
             eh_processo_assinatura = 'assinatura_cliente' in dados or 'assinatura_corretor' in dados or 'realizada' in dados or 'localizacao_assinatura' in dados
             
             if not eh_processo_assinatura:
                 raise PermissionDenied("Não é possível editar os dados de uma visita que já possui assinaturas.")

        if self.request.user.is_superuser:
            serializer.save()
        elif serializer.instance.imobiliaria == tenant:
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar esta visita.")

    def perform_destroy(self, instance):
        if instance.assinatura_cliente or instance.assinatura_corretor:
             raise PermissionDenied("Não é possível excluir uma visita que já foi assinada.")

        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)

        if self.request.user.is_superuser:
            instance.delete()
        elif instance.imobiliaria == tenant:
            instance.delete()
        else:
            raise PermissionDenied("Você não tem permissão para excluir esta visita.")


class AtividadeViewSet(viewsets.ModelViewSet):
    serializer_class = AtividadeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Atividade.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-data_criacao')
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)

        if tenant:
            queryset = queryset.filter(cliente__imobiliaria=tenant)
        elif not self.request.user.is_superuser:
            return Atividade.objects.none()

        return queryset

    def list(self, request, *args, **kwargs):
        cliente_id = request.query_params.get('cliente_id')
        if not cliente_id:
            return Response([])
            
        queryset = self.get_queryset().filter(cliente_id=cliente_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)


class OportunidadeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de Oportunidades (Funil de Vendas).
    Contém lógica avançada de permissões, isolamento de tenant e notificações automáticas.
    """
    serializer_class = OportunidadeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configuração de Filtros de Texto
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'titulo', 
        'cliente__nome', 
        'cliente__razao_social', 
        'cliente__documento',
        'imovel__titulo',
        'imovel__logradouro', 
        'imovel__bairro'
    ]

    def get_queryset(self):
        """
        Sobrescreve o queryset padrão para aplicar regras de negócio:
        1. Isolamento por Tenant (Imobiliária).
        2. Visibilidade baseada em cargo (Admin vs Corretor).
        3. Filtros via URL.
        """
        user = self.request.user
        
        # Define o Tenant atual (via Middleware ou Usuário)
        tenant = getattr(self.request, 'tenant', None) or getattr(user, 'imobiliaria', None)
        
        # Otimiza a busca inicial com select_related para evitar N+1 queries
        base_queryset = Oportunidade.objects.select_related(
            'cliente', 
            'imovel', 
            'responsavel', 
            'fase', 
            'imobiliaria'
        ).order_by('fase__ordem', '-data_criacao')

        # 1. Filtro por Tenant (Isolamento de Dados)
        if user.is_superuser:
            # Superusuário vê tudo, a menos que um tenant seja forçado no contexto
            queryset = base_queryset.filter(imobiliaria=tenant) if tenant else base_queryset
        elif tenant:
            # Usuários normais veem apenas dados da sua imobiliária
            queryset = base_queryset.filter(imobiliaria=tenant)
        else:
            # Usuário sem imobiliária não vê nada (fail-safe)
            return Oportunidade.objects.none()

        # 2. Filtro de Privacidade (Visão do Corretor vs Admin)
        # Verifica flag is_admin ou cargo textual
        is_admin_user = (
            user.is_superuser or 
            getattr(user, 'is_admin', False) or 
            str(getattr(user, 'cargo', '')).upper() in ['ADMIN', 'SUPERADMIN', 'GERENTE']
        )

        # Se NÃO for Admin, vê apenas as oportunidades onde é responsável
        if not is_admin_user:
            queryset = queryset.filter(responsavel=user)

        # 3. Filtros Extras da URL (Ex: ?responsavel=5)
        # Útil para Admins filtrarem o dashboard por corretor
        responsavel_id = self.request.query_params.get('responsavel')
        if responsavel_id:
            try:
                queryset = queryset.filter(responsavel__id=int(responsavel_id))
            except (ValueError, TypeError):
                pass 

        return queryset

    def perform_create(self, serializer):
        """
        Ao criar, associa automaticamente à imobiliária do usuário e define o responsável padrão.
        """
        user = self.request.user
        tenant = getattr(self.request, 'tenant', None) or getattr(user, 'imobiliaria', None)

        # Fallback para Superuser sem tenant (pega a primeira imobiliária para teste)
        if not tenant and user.is_superuser:
             tenant = Imobiliaria.objects.first()
        
        if not tenant:
            raise PermissionDenied("Apenas utilizadores associados a uma imobiliária podem criar oportunidades.")
        
        save_kwargs = {'imobiliaria': tenant}
        
        # Se o payload não trouxer responsável, assume o usuário logado
        if not serializer.validated_data.get('responsavel'):
            save_kwargs['responsavel'] = user
            
        serializer.save(**save_kwargs)

    def perform_update(self, serializer):
        """
        Lógica complexa de atualização:
        1. Verifica permissão de edição.
        2. Gerencia transferência de responsabilidade (Admin override).
        3. Gera notificações e histórico de atividades.
        """
        # 1. Dados Prévios (Snapshot antes de salvar)
        oportunidade = self.get_object()
        fase_anterior = oportunidade.fase.titulo if oportunidade.fase else 'Indefinida'
        responsavel_anterior = oportunidade.responsavel
        
        user = self.request.user
        
        # Verificação de Admin
        is_admin_user = (
            user.is_superuser or 
            getattr(user, 'is_admin', False) or 
            str(getattr(user, 'cargo', '')).upper() in ['ADMIN', 'SUPERADMIN', 'GERENTE']
        )
        
        # 2. Trava de Segurança
        if not is_admin_user and oportunidade.responsavel != user:
             raise PermissionDenied("Você não pode editar uma oportunidade que não lhe pertence.")

        # 3. Salva a instância (Update padrão do DRF)
        instance = serializer.save()

        # 4. FORÇA BRUTA: Atualização do Responsável
        # Necessário pois campos 'read_only' no serializer são ignorados no update padrão.
        # Apenas Admins podem transferir oportunidades de outros.
        if is_admin_user and 'responsavel' in self.request.data:
            try:
                new_resp_data = self.request.data['responsavel']
                new_resp_id = None

                # Normaliza input (pode vir objeto {id: 1} ou int 1)
                if isinstance(new_resp_data, dict):
                    new_resp_id = new_resp_data.get('id')
                elif new_resp_data is not None:
                    try:
                        new_resp_id = int(new_resp_data)
                    except (ValueError, TypeError):
                        pass
                
                # Se detectou uma mudança real de ID
                if new_resp_id and instance.responsavel_id != new_resp_id:
                    # Atualiza direto no banco (Bypass do Serializer)
                    instance.responsavel_id = new_resp_id
                    instance.save(update_fields=['responsavel']) 
                    instance.refresh_from_db() # Atualiza objeto em memória
                    logger.info(f"Oportunidade {instance.id} transferida manualmente pelo Admin {user.id}")

            except Exception as e:
                logger.error(f"ERRO AO TRANSFERIR OPORTUNIDADE: {e}")

        # 5. Lógica de Pós-Processamento (Notificações e Histórico)
        responsavel_novo = instance.responsavel
        
        # A. Notificação de Transferência
        if responsavel_novo and responsavel_novo != responsavel_anterior:
            nome_antigo = responsavel_anterior.get_full_name() or responsavel_anterior.username if responsavel_anterior else 'Ninguém'
            nome_novo = responsavel_novo.get_full_name() or responsavel_novo.username
            
            descricao = f"Oportunidade transferida de '{nome_antigo}' para '{nome_novo}'."
            
            # Registra no histórico do cliente
            Atividade.objects.create(
                cliente=instance.cliente,
                imobiliaria=instance.imobiliaria, # Garante tenant na atividade
                tipo='NOTA',
                descricao=descricao,
                registrado_por=user
            )

            # Notifica o novo dono
            try:
                Notificacao.objects.create(
                    imobiliaria=instance.imobiliaria,
                    destinatario=responsavel_novo,
                    titulo="Nova Oportunidade",
                    mensagem=f"A oportunidade '{instance.titulo}' foi transferida para você.",
                    link=f"/oportunidades/{instance.id}", # Link para frontend
                    tipo='SISTEMA'
                )
            except Exception as e:
                logger.warning(f"Falha ao criar notificação de transferência: {e}")
        
        # B. Notificação de Mudança de Fase
        fase_nova_titulo = instance.fase.titulo if instance.fase else 'Indefinida'
        if fase_nova_titulo != fase_anterior:
            descricao = f"Oportunidade '{instance.titulo}' movida da fase '{fase_anterior}' para '{fase_nova_titulo}'."
            
            Atividade.objects.create(
                cliente=instance.cliente,
                imobiliaria=instance.imobiliaria,
                tipo='MUDANCA_FASE', # Certifique-se que este choice existe no model Atividade
                descricao=descricao,
                registrado_por=user
            )

    @action(detail=False, methods=['get'], url_path='stats')
    def dashboard_stats(self, request):
        """
        Retorna estatísticas para o dashboard principal.
        Endpoint: /api/v1/oportunidades/stats/
        """
        try:
            qs = self.get_queryset()

            # CORREÇÃO: Usar fase__titulo__icontains ou fase__slug__in
            # O erro 500 anterior ocorria porque 'fase' é uma ForeignKey e estávamos comparando com strings.
            # Aqui filtramos pelo campo 'titulo' da tabela relacionada FunilEtapa.
            
            total_ativas = qs.exclude(
                Q(fase__titulo__icontains='Ganho') | 
                Q(fase__titulo__icontains='Perdido') | 
                Q(fase__titulo__icontains='Cancelado') |
                Q(fase__titulo__icontains='Vendido') |
                Q(fase__titulo__icontains='Fechado')
            ).count()

            # Opcional: Soma de valores (se existir campo 'valor')
            # total_valor = qs.exclude(fase__titulo__icontains='Ganho'...).aggregate(Sum('valor'))['valor__sum'] or 0

            return Response({
                "total_ativas": total_ativas,
                # "total_valor": total_valor,
                "status": "success"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro stats oportunidade: {e}")
            return Response(
                {"error": "Erro ao calcular estatísticas", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FunilEtapaViewSet(viewsets.ModelViewSet):
    serializer_class = FunilEtapaSerializer
    permission_classes = [permissions.IsAuthenticated] # CORRIGIDO: Permite visualização para Corretores

    def get_queryset(self):
        user = self.request.user
        tenant = getattr(self.request, 'tenant', None) or getattr(user, 'imobiliaria', None)

        if user.is_superuser:
            if not tenant:
                return FunilEtapa.objects.all().order_by('imobiliaria', 'ordem')
            return FunilEtapa.objects.filter(imobiliaria=tenant).order_by('ordem')
        
        if tenant:
            return FunilEtapa.objects.filter(imobiliaria=tenant, ativa=True).order_by('ordem')
        return FunilEtapa.objects.none()

    def perform_create(self, serializer):
        # Bloqueia criação se não for admin
        if not (self.request.user.is_superuser or getattr(self.request.user, 'is_admin', False)):
             raise PermissionDenied("Apenas administradores podem criar etapas.")

        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)
        if not tenant and self.request.user.is_superuser:
             tenant = Imobiliaria.objects.first()

        if not tenant:
            raise PermissionDenied("Imobiliária não identificada.")
            
        serializer.save(imobiliaria=tenant)

    def perform_update(self, serializer):
        # Bloqueia edição se não for admin
        if not (self.request.user.is_superuser or getattr(self.request.user, 'is_admin', False)):
             raise PermissionDenied("Apenas administradores podem editar etapas.")
             
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)
        if not self.request.user.is_superuser and serializer.instance.imobiliaria != tenant:
            raise PermissionDenied("Permissão negada.")
        serializer.save()

    def perform_destroy(self, instance):
        # Bloqueia exclusão se não for admin
        if not (self.request.user.is_superuser or getattr(self.request.user, 'is_admin', False)):
             raise PermissionDenied("Apenas administradores podem excluir etapas.")
             
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)
        if not self.request.user.is_superuser and instance.imobiliaria != tenant:
            raise PermissionDenied("Permissão negada.")
        instance.delete()


class TarefaViewSet(viewsets.ModelViewSet):
    serializer_class = TarefaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'descricao', 'oportunidade__cliente__nome']

    def get_queryset(self):
        user = self.request.user
        tenant = getattr(self.request, 'tenant', None) or getattr(user, 'imobiliaria', None)

        if user.is_superuser:
            if not tenant:
                queryset = Tarefa.objects.all()
            else:
                queryset = Tarefa.objects.filter(
                    Q(imobiliaria=tenant) | Q(oportunidade__imobiliaria=tenant)
                ).distinct()
        elif tenant:
            # Lógica robusta para encontrar tarefas vinculadas à imobiliária
            # 1. Tarefa tem FK direta para imobiliária
            # 2. Tarefa ligada a Oportunidade da imobiliária
            # 3. Tarefa sem imobiliária (legado/avulsa) mas o dono é da imobiliária
            queryset = Tarefa.objects.filter(
                Q(imobiliaria=tenant) | 
                Q(oportunidade__imobiliaria=tenant) |
                (Q(imobiliaria__isnull=True) & Q(responsavel__imobiliaria=tenant))
            ).distinct()
        else:
            return Tarefa.objects.none()
        
        # Filtros Específicos
        oportunidade_id = self.request.query_params.get('oportunidade')
        if oportunidade_id:
            queryset = queryset.filter(oportunidade_id=oportunidade_id)
            
        responsavel_id = self.request.query_params.get('responsavel')
        if responsavel_id:
            queryset = queryset.filter(responsavel_id=responsavel_id)

        start_date = self.request.query_params.get('start')
        end_date = self.request.query_params.get('end')
        if start_date and end_date:
            queryset = queryset.filter(data_vencimento__range=[start_date, end_date])
            
        return queryset.order_by('data_vencimento')

    @action(detail=False, methods=['get'], url_path='kanban')
    def kanban(self, request):
        """
        Retorna tarefas formatadas para quadro Kanban/Calendário.
        Filtra tarefas muito antigas se já concluídas para não poluir a view.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        if not request.query_params.get('start'):
            trinta_dias_atras = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(
                Q(status__in=['pendente', 'em_andamento']) |
                (Q(status='concluida') & Q(data_vencimento__gte=trinta_dias_atras))
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def dashboard_stats(self, request):
        """
        Endpoint para estatísticas de tarefas no dashboard principal.
        Retorna: Total Pendente e Lista das 5 tarefas para hoje.
        """
        try:
            qs = self.get_queryset()
            hoje = timezone.now().date()
            
            # 1. Contagem de Pendências (Tudo que não está concluído)
            pendentes = qs.exclude(status='concluida').count()
            
            # 2. Tarefas de Hoje (Para o Widget de Lista)
            # Filtra tarefas que vencem hoje e não estão prontas
            tarefas_hoje = qs.filter(
                data_vencimento__date=hoje
            ).exclude(status='concluida').order_by('data_vencimento')[:5]
            
            # Serializa a lista curta para o widget
            # Usamos uma serialização simplificada aqui para performance
            dados_hoje = []
            for t in tarefas_hoje:
                cliente_nome = "Sem cliente"
                if t.oportunidade and t.oportunidade.cliente:
                    cliente_nome = t.oportunidade.cliente.nome
                
                dados_hoje.append({
                    "id": t.id,
                    "titulo": t.titulo,
                    "data_vencimento": t.data_vencimento,
                    "cliente_nome": cliente_nome,
                    "prioridade": t.prioridade
                })

            return Response({
                "pendentes": pendentes,
                "hoje": dados_hoje
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "Erro ao calcular stats tarefas", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='listar-responsaveis')
    def listar_responsaveis(self, request):
        user = request.user
        tenant = getattr(request, 'tenant', None) or getattr(user, 'imobiliaria', None)
        
        if tenant:
            users = User.objects.filter(imobiliaria=tenant, is_active=True)
        else:
            users = User.objects.filter(is_active=True)
            
        serializer = UsuarioSimplesSerializer(users, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        oportunidade_id = self.request.data.get('oportunidade_id') or self.request.data.get('oportunidade')
        oportunidade = None
        
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)

        if not tenant and self.request.user.is_superuser:
             tenant = Imobiliaria.objects.first()

        if oportunidade_id:
            # Verifica se a oportunidade pertence ao tenant
            oportunidade = get_object_or_404(Oportunidade, pk=oportunidade_id)
            if not (self.request.user.is_superuser or oportunidade.imobiliaria == tenant):
                raise PermissionDenied("Você não tem permissão para adicionar tarefas a esta oportunidade.")
        
        save_kwargs = {
            'oportunidade': oportunidade,
            'imobiliaria': tenant
        }

        # Se não enviou responsável, define o usuário atual
        if not serializer.validated_data.get('responsavel'):
            save_kwargs['responsavel'] = self.request.user

        tarefa = serializer.save(**save_kwargs)
        
        # Integração Google Calendar
        if tarefa.responsavel and getattr(tarefa.responsavel, 'google_calendar_token', None):
            try:
                agendar_tarefa_no_calendario(tarefa)
            except Exception:
                pass # Falha no calendário não deve quebrar a criação da tarefa
    
    def perform_update(self, serializer):
        instance = self.get_object()
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)

        # Verificação de segurança de Tenancy no Update
        eh_do_tenant = False
        if instance.imobiliaria == tenant:
            eh_do_tenant = True
        elif instance.oportunidade and instance.oportunidade.imobiliaria == tenant:
            eh_do_tenant = True
        elif instance.imobiliaria is None and instance.responsavel.imobiliaria == tenant:
            eh_do_tenant = True

        if not (self.request.user.is_superuser or eh_do_tenant):
            raise PermissionDenied("Você não tem permissão para atualizar esta tarefa.")
            
        tarefa = serializer.save()
        
        # Integração Google Calendar (Update)
        if tarefa.responsavel and getattr(tarefa.responsavel, 'google_calendar_token', None):
            try:
                agendar_tarefa_no_calendario(tarefa, editar=True)
            except Exception:
                pass

class MinhasTarefasView(viewsets.ReadOnlyModelViewSet):
    serializer_class = TarefaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Tarefa.objects.filter(responsavel=self.request.user)
        
        start_date_str = self.request.query_params.get('start', None)
        end_date_str = self.request.query_params.get('end', None)
        
        if start_date_str and end_date_str:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if start_date and end_date:
                queryset = queryset.filter(data_vencimento__date__gte=start_date, data_vencimento__date__lte=end_date)
        
        return queryset.order_by('data_vencimento')

class RelatoriosView(viewsets.ViewSet):
    permission_classes = [IsAdminOrSuperUser]

    def list(self, request):
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'imobiliaria', None)

        if not tenant and request.user.is_superuser:
            tenant = Imobiliaria.objects.first()
        
        if not tenant:
            return Response({"error": "Nenhuma imobiliária associada."}, status=status.HTTP_400_BAD_REQUEST)
        
        relatorio_tipo = request.query_params.get('tipo', 'oportunidades_funil')

        if relatorio_tipo == 'oportunidades_funil':
            data = self._get_oportunidades_funil(tenant)
        elif relatorio_tipo == 'origem_leads':
            data = self._get_origem_leads(tenant)
        elif relatorio_tipo == 'desempenho_corretores':
            data = self._get_desempenho_corretores(tenant) 
        elif relatorio_tipo == 'imobiliaria':
            data = self._get_relatorio_imobiliaria(tenant)
        elif relatorio_tipo == 'valor_estimado_aberto':
            data = self._get_valor_estimado_aberto(tenant)
        else:
            return Response({"error": "Tipo de relatório inválido."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data)

    def _get_oportunidades_funil(self, tenant):
        funil = Oportunidade.objects.filter(imobiliaria=tenant)\
            .values('fase__titulo')\
            .annotate(total=Count('fase'))\
            .order_by('fase__ordem')
        return list(funil)

    def _get_origem_leads(self, tenant):
        origens = Oportunidade.objects.filter(imobiliaria=tenant).values('fonte').annotate(total=Count('fonte'))
        return list(origens)

    def _get_desempenho_corretores(self, tenant):
        return {"message": "Relatório de desempenho de corretores."}
    
    def _get_relatorio_imobiliaria(self, tenant):
         return {"message": "Relatório de imobiliária."}
         
    def _get_valor_estimado_aberto(self, tenant):
        soma = Oportunidade.objects.filter(
            imobiliaria=tenant
        ).exclude(
            Q(fase__probabilidade_fechamento=100) | Q(fase__probabilidade_fechamento=0)
        ).aggregate(total=Coalesce(Sum('valor_estimado'), 0.0, output_field=models.DecimalField()))
        
        return {"valor_total_aberto": soma['total']}

class GerarRelatorioVisitaPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'imobiliaria', None)

        if request.user.is_superuser:
            if not tenant:
                 visita = get_object_or_404(Visita, pk=pk)
            else:
                 visita = get_object_or_404(Visita, pk=pk, imobiliaria=tenant)
        elif tenant:
            visita = get_object_or_404(Visita, pk=pk, imobiliaria=tenant)
        else:
            return HttpResponse("Visita não encontrada ou acesso negado.", status=404)

        logo_b64 = None
        if visita.imobiliaria and hasattr(visita.imobiliaria, 'foto_perfil'):
            logo_b64 = image_to_base64(visita.imobiliaria.foto_perfil)

        assinatura_corretor_b64 = image_to_base64(visita.assinatura_corretor)
        assinatura_cliente_b64 = image_to_base64(visita.assinatura_cliente)

        context = {
            'visita': visita,
            'cliente': visita.cliente,
            'imobiliaria': visita.imobiliaria,
            'imoveis': visita.imoveis.all(),
            'data_impressao': timezone.now(),
            'corretor': visita.corretor if visita.corretor else request.user,
            'logo_b64': logo_b64,
            'assinatura_corretor_b64': assinatura_corretor_b64,
            'assinatura_cliente_b64': assinatura_cliente_b64,
        }

        html_string = render_to_string('relatorio_visita_template.html', context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result, encoding='UTF-8')

        if not pdf.err:
            filename = f'ficha_visita_{visita.id}_{visita.cliente.nome.replace(" ", "_")}.pdf'
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        else:
            return HttpResponse(f"Erro ao gerar PDF", status=500)
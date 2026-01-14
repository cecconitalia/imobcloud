# C:\wamp64\www\imobcloud\app_clientes\views.py

import os
import json
import logging
from io import BytesIO
from datetime import date

from django.conf import settings
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth, Coalesce
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.timezone import localdate, timedelta
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.core.files.storage import default_storage
from django.template.loader import render_to_string

from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView

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
# HELPER PARA VERIFICAR PERMISSÕES
# ====================================================================
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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            if not getattr(user, 'google_json_file', None):
                return Response({"error": "Nenhum arquivo de credenciais do Google foi encontrado."}, status=status.HTTP_400_BAD_REQUEST)
            
            json_file_path = default_storage.path(user.google_json_file.name)
            
            flow = Flow.from_client_secrets_file(
                json_file_path,
                scopes=SCOPES,
                redirect_uri=request.build_absolute_uri(reverse('google-calendar-auth-callback'))
            )
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
    
            request.session['oauth_state'] = state
            return HttpResponseRedirect(authorization_url)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GoogleCalendarAuthCallbackView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        state = request.session.pop('oauth_state', None)
        if not state or state != request.query_params.get('state'):
            return HttpResponse("Estado inválido. O processo de autenticação falhou.", status=400)
        
        try:
            user = request.user
            if not getattr(user, 'google_json_file', None):
                 return HttpResponse("Erro: Arquivo de credenciais não encontrado no usuário.", status=400)

            json_file_path = default_storage.path(user.google_json_file.name)
    
            flow = Flow.from_client_secrets_file(
                json_file_path,
                scopes=SCOPES,
                redirect_uri=request.build_absolute_uri(reverse('google-calendar-auth-callback'))
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
            
            return HttpResponse("Conexão com o Google Calendar realizada com sucesso!")
        except Exception as e:
            logger.error(f"Erro Google Calendar Callback: {e}")
            return HttpResponse(f"Erro ao processar o callback.", status=400)

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
                # Fallback para a primeira imobiliária (apenas dev/teste)
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
        finalidade = request.query_params.get('finalidade') 
        
        if not finalidade:
            return Response([], status=status.HTTP_400_BAD_REQUEST)
        
        # Filtra clientes que são proprietários E possuem imóveis com a finalidade desejada (venda/aluguel)
        queryset = base_queryset.filter(
            perfil_cliente__contains=['PROPRIETARIO'],
            imoveis_propriedade__status=finalidade 
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

        # Tenta deduzir imobiliária pelo imóvel se for superuser e sem tenant fixo
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
             eh_processo_assinatura = 'assinatura_cliente' in dados or 'assinatura_corretor' in dados
             
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
    # Carregar 'fase' no select_related é importante se fase for ForeignKey
    queryset = Oportunidade.objects.all().select_related('cliente', 'imovel', 'responsavel', 'fase')
    serializer_class = OportunidadeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'titulo', 
        'cliente__nome', 
        'cliente__razao_social', 
        'imovel__logradouro', 
        'imovel__bairro'
    ]

    def get_queryset(self):
        user = self.request.user
        tenant = getattr(self.request, 'tenant', None) or getattr(user, 'imobiliaria', None)
        base_queryset = Oportunidade.objects.select_related('fase', 'cliente', 'responsavel')

        if user.is_superuser:
            queryset = base_queryset.filter(imobiliaria=tenant) if tenant else base_queryset
        elif tenant:
            queryset = base_queryset.filter(imobiliaria=tenant)
        else:
            return Oportunidade.objects.none()

        responsavel_id = self.request.query_params.get('responsavel')
        if responsavel_id:
            try:
                queryset = queryset.filter(responsavel__id=int(responsavel_id))
            except ValueError:
                pass 

        # Ordenação por ordem da etapa (se FK) e data
        return queryset.order_by('fase__ordem', 'data_criacao')

    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)

        if not tenant and self.request.user.is_superuser:
             tenant = Imobiliaria.objects.first()
        
        if not tenant:
            raise PermissionDenied("Apenas utilizadores associados a uma imobiliária podem criar oportunidades.")
        
        save_kwargs = {'imobiliaria': tenant}
        if not serializer.validated_data.get('responsavel'):
            save_kwargs['responsavel'] = self.request.user
            
        serializer.save(**save_kwargs)
    
    def perform_update(self, serializer):
        oportunidade = self.get_object()
        
        # Captura estado anterior
        fase_anterior = oportunidade.fase.titulo if oportunidade.fase else 'Indefinida'
        responsavel_anterior = oportunidade.responsavel
        
        instance = serializer.save()

        # 1. Notificação de transferência de responsável
        responsavel_novo = instance.responsavel
        if responsavel_novo and responsavel_novo != responsavel_anterior:
            responsavel_anterior_nome = responsavel_anterior.first_name if responsavel_anterior else 'Ninguém'
            
            descricao = f"Oportunidade transferida de '{responsavel_anterior_nome}' para '{responsavel_novo.first_name}'."
            
            Atividade.objects.create(
                cliente=instance.cliente,
                tipo='NOTA',
                descricao=descricao,
                registrado_por=self.request.user
            )

            Notificacao.objects.create(
                destinatario=responsavel_novo,
                mensagem=f"A oportunidade '{instance.titulo}' foi transferida para si.",
                link=f"/oportunidades/editar/{instance.id}"
            )
        
        # 2. Log de mudança de fase
        fase_nova_titulo = instance.fase.titulo if instance.fase else 'Indefinida'
        
        if fase_nova_titulo != fase_anterior:
            descricao = f"Oportunidade '{instance.titulo}' movida da fase '{fase_anterior}' para '{fase_nova_titulo}'."
            Atividade.objects.create(
                cliente=instance.cliente,
                tipo='MUDANCA_FASE',
                descricao=descricao,
                registrado_por=self.request.user
            )


class FunilEtapaViewSet(viewsets.ModelViewSet):
    serializer_class = FunilEtapaSerializer
    permission_classes = [IsAdminOrSuperUser]

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
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)

        if not self.request.user.is_superuser and not tenant:
            raise PermissionDenied("Permissão negada.")
        
        if not tenant and self.request.user.is_superuser:
             tenant = Imobiliaria.objects.first()

        if not tenant:
            raise PermissionDenied("Imobiliária não identificada.")
            
        serializer.save(imobiliaria=tenant)

    def perform_update(self, serializer):
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)
        if not self.request.user.is_superuser and serializer.instance.imobiliaria != tenant:
            raise PermissionDenied("Permissão negada.")
        serializer.save()

    def perform_destroy(self, instance):
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
            queryset = Tarefa.objects.filter(
                Q(imobiliaria=tenant) | 
                Q(oportunidade__imobiliaria=tenant) |
                (Q(imobiliaria__isnull=True) & Q(responsavel__imobiliaria=tenant))
            ).distinct()
        else:
            return Tarefa.objects.none()
        
        # Filtros Adicionais
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
        queryset = self.filter_queryset(self.get_queryset())
        
        # Otimização: Filtrar concluídas antigas apenas se não houver filtro de data explícito
        if not request.query_params.get('start'):
            trinta_dias_atras = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(
                Q(status__in=['pendente', 'em_andamento']) |
                (Q(status='concluida') & Q(data_vencimento__gte=trinta_dias_atras))
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
            oportunidade = get_object_or_404(Oportunidade, pk=oportunidade_id)
            if not (self.request.user.is_superuser or oportunidade.imobiliaria == tenant):
                raise PermissionDenied("Você não tem permissão para adicionar tarefas a esta oportunidade.")
        
        save_kwargs = {
            'oportunidade': oportunidade,
            'imobiliaria': tenant
        }

        # Se nenhum responsável foi indicado, assume o usuário logado
        if not serializer.validated_data.get('responsavel'):
            save_kwargs['responsavel'] = self.request.user

        tarefa = serializer.save(**save_kwargs)
        
        # Tenta agendar no Google Calendar se configurado
        if tarefa.responsavel and getattr(tarefa.responsavel, 'google_calendar_token', None):
            try:
                agendar_tarefa_no_calendario(tarefa)
            except Exception:
                pass # Falha silenciosa ou logar em produção
    
    def perform_update(self, serializer):
        instance = self.get_object()
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)

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
        # Agrupa por título da fase dinâmica
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
        # Considera aberto se probabilidade > 0 e < 100
        soma = Oportunidade.objects.filter(
            imobiliaria=tenant
        ).exclude(
            Q(fase__probabilidade_fechamento=100) | Q(fase__probabilidade_fechamento=0)
        ).aggregate(total=Coalesce(Sum('valor_estimado'), 0.0, output_field=models.DecimalField()))
        
        return {"valor_total_aberto": soma['total']}

# ====================================================================
# VIEW PARA GERAR PDF DA VISITA (Ficha de Visita)
# ====================================================================
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

        context = {
            'visita': visita,
            'cliente': visita.cliente,
            'imobiliaria': visita.imobiliaria,
            'imoveis': visita.imoveis.all(),
            'data_impressao': timezone.now(),
            'corretor': visita.corretor if visita.corretor else request.user,
            'logo_url': None
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
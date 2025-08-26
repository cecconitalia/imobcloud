# C:\wamp64\www\ImobCloud\app_clientes\views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework import filters
from django.db.models import Count, Q
from django.utils.timezone import localdate
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from google_auth_oauthlib.flow import Flow
import os
import json
import pickle
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Sum

from core.models import PerfilUsuario, Notificacao, Imobiliaria
from core.permissions import IsAdminOrSuperUser
from .models import Oportunidade, Tarefa, Cliente, Visita, Atividade, FunilEtapa
from .serializers import (
    OportunidadeSerializer,
    FunilVendasSerializer,
    TarefaSerializer,
    RelatorioCorretorSerializer,
    RelatorioOrigemSerializer,
    RelatorioImobiliariaSerializer,
    ClienteSerializer,
    VisitaSerializer,
    AtividadeSerializer,
    FunilEtapaSerializer,
)
from ImobCloud.utils.google_calendar_api import agendar_tarefa_no_calendario
from app_imoveis.models import Imovel

User = get_user_model()

# ====================================================================
# VIEWS DO GOOGLE CALENDAR (Mantidas como estavam)
# ====================================================================
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_DIR = os.path.join(settings.MEDIA_ROOT, 'google_credentials')

class GoogleCalendarAuthView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            perfil = request.user.perfil
            if not perfil.google_json_file:
                return Response({"error": "Nenhum arquivo de credenciais do Google foi encontrado."}, status=status.HTTP_400_BAD_REQUEST)
            
            json_file_path = default_storage.path(perfil.google_json_file.name)
            
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
        except PerfilUsuario.DoesNotExist:
            return Response({"error": "O utilizador não tem um perfil associado."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GoogleCalendarAuthCallbackView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        state = request.session.pop('oauth_state', None)
        if not state or state != request.query_params.get('state'):
            return HttpResponse("Estado inválido. O processo de autenticação falhou.", status=400)
        
        try:
            json_file_path = default_storage.path(request.user.perfil.google_json_file.name)
    
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
            
            request.user.perfil.google_calendar_token = json.dumps(credentials_json)
            request.user.perfil.save()
            
            return HttpResponse("Conexão com o Google Calendar realizada com sucesso!")
        except PerfilUsuario.DoesNotExist:
            return HttpResponse("Erro: O utilizador não tem um perfil associado.", status=400)
        except Exception as e:
            return HttpResponse(f"Erro ao processar o callback: {e}", status=400)

# ====================================================================
# VIEWS DO CRM (Com correções)
# ====================================================================

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome_completo', 'cpf_cnpj', 'email']

    def get_queryset(self):
        base_queryset = Cliente.objects.filter(ativo=True)
        if self.request.user.is_superuser:
            return base_queryset.all()
        elif self.request.tenant:
            return base_queryset.filter(imobiliaria=self.request.tenant)
        return Cliente.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            if 'imobiliaria' in self.request.data:
                imobiliaria_id = self.request.data['imobiliaria']
                imobiliaria_obj = get_object_or_404(Imobiliaria, pk=imobiliaria_id)
                serializer.save(imobiliaria=imobiliaria_obj)
            else:
                raise PermissionDenied("Para superusuário, a imobiliária é obrigatória.")
        else:
            if not self.request.tenant:
                raise PermissionDenied("Não foi possível associar o cliente a uma imobiliária. Tenant não identificado ou sem permissão.")
            serializer.save(imobiliaria=self.request.tenant)

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar este cliente.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and instance.imobiliaria == self.request.tenant):
            instance.ativo = False
            instance.save()
        else:
            raise PermissionDenied("Você não tem permissão para inativar este cliente.")

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
        if self.request.user.is_superuser:
            return Visita.objects.all()
        elif self.request.tenant:
            return Visita.objects.filter(imobiliaria=self.request.tenant)
        return Visita.objects.none()

    def perform_create(self, serializer):
        imovel_id = self.request.data.get('imovel')
        cliente_id = self.request.data.get('cliente')
        imovel = get_object_or_404(Imovel, pk=imovel_id)
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        
        if self.request.user.is_superuser:
            imobiliaria_obj = imovel.imobiliaria
            serializer.save(imobiliaria=imobiliaria_obj, cliente=cliente, imovel=imovel)
        elif hasattr(self.request.user, 'perfil') and self.request.tenant:
            serializer.save(imobiliaria=self.request.tenant, cliente=cliente, imovel=imovel)
        else:
            raise PermissionDenied("Não foi possível associar a visita. Tenant não identificado ou inválido.")

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar esta visita.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser:
            instance.delete()
        elif hasattr(self.request.user, 'perfil') and instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise PermissionDenied("Você não tem permissão para excluir esta visita.")


class AtividadeViewSet(viewsets.ModelViewSet):
    queryset = Atividade.objects.all()
    serializer_class = AtividadeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Atividade.objects.all()
        elif hasattr(user, 'perfil') and user.perfil.imobiliaria:
            return Atividade.objects.filter(cliente__imobiliaria=user.perfil.imobiliaria)
        return Atividade.objects.none()

    def perform_create(self, serializer):
        cliente_id = self.request.data.get('cliente')
        cliente = get_object_or_404(Cliente, pk=cliente_id)

        if not (self.request.user.is_superuser or cliente.imobiliaria == self.request.tenant):
            raise PermissionDenied("Você não tem permissão para adicionar atividades a este cliente.")

        serializer.save(cliente=cliente, registrado_por=self.request.user)


class OportunidadeViewSet(viewsets.ModelViewSet):
    queryset = Oportunidade.objects.all().select_related('cliente', 'imovel', 'responsavel__user')
    serializer_class = OportunidadeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_queryset = Oportunidade.objects.all()

        if user.is_superuser:
            return base_queryset
        
        if self.request.tenant:
            queryset = base_queryset.filter(imobiliaria=self.request.tenant)
            if hasattr(user, 'perfil') and user.perfil.cargo == PerfilUsuario.Cargo.CORRETOR:
                queryset = queryset.filter(responsavel=user)
            return queryset

        return Oportunidade.objects.none()

    def perform_create(self, serializer):
        if not self.request.tenant:
            raise PermissionDenied("Apenas utilizadores associados a uma imobiliária podem criar oportunidades.")
        
        if not hasattr(self.request.user, 'perfil'):
            raise PermissionDenied("O seu utilizador não tem um perfil de corretor associado.")
            
        serializer.save(imobiliaria=self.request.tenant, responsavel=self.request.user)
    
    def perform_update(self, serializer):
        oportunidade = self.get_object()
        responsavel_anterior = oportunidade.responsavel
        
        instance = serializer.save()

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
    
    def partial_update(self, request, *args, **kwargs):
        oportunidade = self.get_object()
        fase_anterior = oportunidade.get_fase_display()
        
        response = super().partial_update(request, *args, **kwargs)

        fase_nova_key = request.data.get('fase')
        if fase_nova_key and fase_nova_key != oportunidade.fase:
            oportunidade.refresh_from_db()
            fase_nova = oportunidade.get_fase_display()
            
            descricao = f"Oportunidade '{oportunidade.titulo}' movida da fase '{fase_anterior}' para '{fase_nova}'."
            
            Atividade.objects.create(
                cliente=oportunidade.cliente,
                tipo='MUDANCA_FASE',
                descricao=descricao,
                registrado_por=request.user
            )
        
        return response


# --- ADICIONADO: VIEWSET PARA AS ETAPAS DO FUNIL ---
class FunilEtapaViewSet(viewsets.ModelViewSet):
    serializer_class = FunilEtapaSerializer
    permission_classes = [IsAdminOrSuperUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return FunilEtapa.objects.all().order_by('imobiliaria', 'ordem')
        
        if self.request.tenant:
            return FunilEtapa.objects.filter(imobiliaria=self.request.tenant, ativa=True).order_by('ordem')
        return FunilEtapa.objects.none()

    def perform_create(self, serializer):
        if not self.request.user.is_superuser and not self.request.tenant:
            raise PermissionDenied("Permissão negada.")
        
        if not self.request.tenant:
            raise PermissionDenied("Imobiliária não identificada.")
            
        serializer.save(imobiliaria=self.request.tenant)

    def perform_update(self, serializer):
        if not self.request.user.is_superuser and serializer.instance.imobiliaria != self.request.tenant:
            raise PermissionDenied("Permissão negada.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_superuser and instance.imobiliaria != self.request.tenant:
            raise PermissionDenied("Permissão negada.")
        instance.delete()


class TarefaViewSet(viewsets.ModelViewSet):
    serializer_class = TarefaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        tenant = self.request.tenant

        if user.is_superuser:
            return Tarefa.objects.all()

        queryset = Tarefa.objects.filter(oportunidade__imobiliaria=tenant)
        return queryset

    def perform_create(self, serializer):
        oportunidade_id = self.request.data.get('oportunidade')
        oportunidade = None
        if oportunidade_id:
            oportunidade = get_object_or_404(Oportunidade, pk=oportunidade_id)
            if not (self.request.user.is_superuser or oportunidade.imobiliaria == self.request.tenant):
                raise PermissionDenied("Você não tem permissão para adicionar tarefas a esta oportunidade.")
        
        tarefa = serializer.save(oportunidade=oportunidade, responsavel=self.request.user)

        if tarefa.responsavel and hasattr(tarefa.responsavel, 'perfil') and tarefa.responsavel.perfil.google_calendar_token:
            try:
                agendar_tarefa_no_calendario(tarefa)
            except Exception as e:
                print(f"Erro ao agendar tarefa no Google Calendar: {e}")
    
    def perform_update(self, serializer):
        instance = self.get_object()
        if not (self.request.user.is_superuser or (instance.oportunidade.imobiliaria == self.request.tenant)):
            raise PermissionDenied("Você não tem permissão para atualizar esta tarefa.")
            
        tarefa = serializer.save()
        if tarefa.responsavel and hasattr(tarefa.responsavel, 'perfil') and tarefa.responsavel.perfil.google_calendar_token:
            try:
                agendar_tarefa_no_calendario(tarefa, editar=True)
            except Exception as e:
                print(f"Erro ao atualizar tarefa no Google Calendar: {e}")

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
                # CORREÇÃO: Usar 'data_vencimento' em vez de 'data_conclusao'
                queryset = queryset.filter(data_vencimento__date__gte=start_date, data_vencimento__date__lte=end_date)
        
        # CORREÇÃO: Usar 'data_vencimento' em vez de 'data_conclusao'
        return queryset.order_by('data_vencimento')

class RelatoriosView(viewsets.ViewSet):
    permission_classes = [IsAdminOrSuperUser]

    def list(self, request):
        tenant = request.tenant
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
        else:
            return Response({"error": "Tipo de relatório inválido."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data)

    def _get_oportunidades_funil(self, tenant):
        funil = Oportunidade.objects.filter(imobiliaria=tenant).values('fase').annotate(total=Count('fase'))
        return list(funil)

    def _get_origem_leads(self, tenant):
        origens = Cliente.objects.filter(imobiliaria=tenant).values('fonte').annotate(total=Count('fonte'))
        return list(origens)

    def _get_desempenho_corretores(self, tenant):
        corretores_desempenho = PerfilUsuario.objects.filter(imobiliaria=tenant, cargo=PerfilUsuario.Cargo.CORRETOR).annotate(
            oportunidades_abertas=Count('oportunidades_responsavel', filter=Q(oportunidades_responsavel__fase__in=['LEAD', 'CONTATO', 'VISITA', 'PROPOSTA', 'NEGOCIACAO'])),
            oportunidades_ganhas=Count('oportunidades_responsavel', filter=Q(oportunidades_responsavel__fase='GANHO')),
            oportunidades_perdidas=Count('oportunidades_responsavel', filter=Q(oportunidades_responsavel__fase='PERDIDO'))
        )
        serializer = RelatorioCorretorSerializer(corretores_desempenho, many=True)
        return serializer.data

    def _get_relatorio_imobiliaria(self, tenant):
        hoje = timezone.localdate()
        primeiro_dia_mes = hoje.replace(day=1)
        
        oportunidades_mes = Oportunidade.objects.filter(
            imobiliaria=tenant,
            data_criacao__date__gte=primeiro_dia_mes
        )
        
        sumario = oportunidades_mes.aggregate(
            novas_oportunidades=Count('id'),
            oportunidades_ganhas=Count('id', filter=Q(fase='GANHO')),
            oportunidades_perdidas=Count('id', filter=Q(fase='PERDIDO'))
        )
        
        oportunidades_por_mes = Oportunidade.objects.filter(imobiliaria=tenant, data_criacao__year=hoje.year)\
            .annotate(mes=TruncMonth('data_criacao'))\
            .values('mes')\
            .annotate(
                ganhas=Count('id', filter=Q(fase='GANHO')),
                perdidas=Count('id', filter=Q(fase='PERDIDO')),
                abertas=Count('id', filter=Q(fase__in=['LEAD', 'CONTATO', 'VISITA', 'PROPOSTA', 'NEGOCIACAO']))
            )\
            .order_by('mes')

        dados = {
            'sumario_mes_atual': sumario,
            'oportunidades_por_mes': list(oportunidades_por_mes)
        }
        
        return dados
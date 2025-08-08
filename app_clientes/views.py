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
from .models import Oportunidade, Tarefa, Cliente, Visita, Atividade
from .serializers import (
    OportunidadeSerializer,
    FunilVendasSerializer,
    TarefaSerializer,
    RelatorioCorretorSerializer,
    RelatorioOrigemSerializer,
    RelatorioImobiliariaSerializer,
    ClienteSerializer,
    VisitaSerializer,
    AtividadeSerializer
)
from ImobCloud.utils.google_calendar_api import agendar_tarefa_no_calendario
from app_imoveis.models import Imovel

User = get_user_model()

# ====================================================================
# VIEWS DO GOOGLE CALENDAR
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
# VIEWS DO CRM
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
                imobiliaria_obj = get_object_or_404(self.request.tenant._meta.model, pk=imobiliaria_id)
                serializer.save(imobiliaria=imobiliaria_obj)
            else:
                raise Exception("Para superusuário, a imobiliária é obrigatória.")
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR]:
            serializer.save(imobiliaria=self.request.tenant)
        else:
            raise Exception("Não foi possível associar o cliente a uma imobiliária. Tenant não identificado ou sem permissão.")

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este cliente.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and instance.imobiliaria == self.request.tenant):
            instance.ativo = False
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise Exception("Você não tem permissão para inativar este cliente.")

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
        if self.request.user.is_superuser:
            imovel_id = self.request.data.get('imovel')
            cliente_id = self.request.data.get('cliente')
            imovel = get_object_or_404(Imovel, pk=imovel_id)
            cliente = get_object_or_404(Cliente, pk=cliente_id)
            if 'imobiliaria' in self.request.data:
                imobiliaria_obj = get_object_or_404(self.request.tenant._meta.model, pk=self.request.data['imobiliaria'])
                serializer.save(imobiliaria=imobiliaria_obj, cliente=cliente, imovel=imovel)
            else:
                raise Exception("Para superusuário, a imobiliária é obrigatória.")
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR]:
            imovel_id = self.request.data.get('imovel')
            cliente_id = self.request.data.get('cliente')
            imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)
            cliente = get_object_or_404(Cliente, pk=cliente_id, imobiliaria=self.request.tenant)
            serializer.save(imobiliaria=self.request.tenant, cliente=cliente, imovel=imovel)
        else:
            raise Exception("Não foi possível associar a visita. Tenant não identificado ou inválido.")

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar esta visita.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser:
            instance.delete()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir esta visita.")


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
            raise PermissionError("Você não tem permissão para adicionar atividades a este cliente.")

        serializer.save(cliente=cliente, registrado_por=self.request.user)


class OportunidadeViewSet(viewsets.ModelViewSet):
    queryset = Oportunidade.objects.all().select_related('cliente', 'imovel', 'responsavel__perfil')
    serializer_class = OportunidadeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = Oportunidade.objects.all()
        elif self.request.tenant:
            if hasattr(user, 'perfil'):
                if user.perfil.cargo == PerfilUsuario.Cargo.ADMIN:
                    queryset = Oportunidade.objects.filter(imobiliaria=self.request.tenant)
                elif user.perfil.cargo == PerfilUsuario.Cargo.CORRETOR:
                    queryset = Oportunidade.objects.filter(imobiliaria=self.request.tenant, responsavel=user)
            else:
                return Oportunidade.objects.none()

            cliente_id = self.request.query_params.get('cliente_id', None)
            if cliente_id:
                queryset = queryset.filter(cliente__id=cliente_id)
            
            return queryset.all()

        return Oportunidade.objects.none()

    def perform_create(self, serializer):
        if not self.request.tenant:
            raise PermissionError("Apenas utilizadores associados a uma imobiliária podem criar oportunidades.")
        serializer.save(imobiliaria=self.request.tenant, responsavel=self.request.user)
    
    def partial_update(self, request, *args, **kwargs):
        oportunidade = self.get_object()
        fase_anterior = oportunidade.get_fase_display()
        fase_nova_key = request.data.get('fase')

        response = super().partial_update(request, *args, **kwargs)

        if fase_nova_key and fase_nova_key != oportunidade.fase:
            oportunidade.refresh_from_db()
            fase_nova = oportunidade.get_fase_display()
            
            descricao = f"Oportunidade '{oportunidade.titulo}' movida da fase '{fase_anterior}' para '{fase_nova}'."
            Atividade.objects.create(
                cliente=oportunidade.cliente,
                tipo='NOTA',
                descricao=descricao,
                registrado_por=request.user
            )
        
        return response

    @action(detail=True, methods=['post'], url_path='transferir')
    def transferir_responsavel(self, request, pk=None):
        oportunidade = self.get_object()
        user = request.user
        
        if not (user.is_superuser or (hasattr(user, 'perfil') and user.perfil.cargo == PerfilUsuario.Cargo.ADMIN) or (oportunidade.responsavel == user)):
            return Response(
                {"detail": "Você não tem permissão para transferir esta oportunidade."},
                status=status.HTTP_403_FORBIDDEN
            )

        novo_corretor_id = request.data.get('novo_corretor')
        if not novo_corretor_id:
            return Response(
                {"detail": "ID do novo corretor é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            novo_corretor = User.objects.get(pk=novo_corretor_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Novo corretor não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        corretor_anterior_nome = oportunidade.responsavel.first_name if oportunidade.responsavel else 'N/A'
        corretor_anterior_username = oportunidade.responsavel.username if oportunidade.responsavel else 'N/A'
        
        oportunidade.responsavel = novo_corretor
        oportunidade.save(update_fields=['responsavel'])
        
        descricao = f"Oportunidade '{oportunidade.titulo}' transferida de '{corretor_anterior_nome}' ({corretor_anterior_username}) para '{novo_corretor.first_name}' ({novo_corretor.username})."
        Atividade.objects.create(
            cliente=oportunidade.cliente,
            tipo='NOTA',
            descricao=descricao,
            registrado_por=user
        )

        Notificacao.objects.create(
            destinatario=novo_corretor,
            mensagem=f"A oportunidade '{oportunidade.titulo}' foi transferida para você.",
            link=f"/oportunidades/editar/{oportunidade.id}"
        )

        return Response(
            {"detail": "Oportunidade transferida com sucesso."},
            status=status.HTTP_200_OK
        )


class TarefaViewSet(viewsets.ModelViewSet):
    serializer_class = TarefaSerializer

    def get_queryset(self):
        user = self.request.user
        tenant = self.request.tenant

        if user.is_superuser:
            return Tarefa.objects.all()

        # CORREÇÃO: Filtrar as tarefas através do perfil do responsável.
        # O modelo Tarefa não tem um campo 'tenant' direto.
        queryset = Tarefa.objects.filter(responsavel__perfil__imobiliaria=tenant)

        oportunidade_id = self.kwargs.get('oportunidade_oportunidade_pk')
        if oportunidade_id:
            queryset = queryset.filter(oportunidade__id=oportunidade_id)
        
        return queryset

    def perform_create(self, serializer):
        if 'oportunidade_pk' in self.kwargs:
            oportunidade = get_object_or_404(Oportunidade, pk=self.kwargs['oportunidade_pk'])
            if not (self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and oportunidade.imobiliaria == self.request.tenant)):
                raise PermissionDenied("Você não tem permissão para adicionar tarefas a esta oportunidade.")
            tarefa = serializer.save(oportunidade=oportunidade, responsavel=self.request.user)
        else:
            if not self.request.tenant:
                raise PermissionDenied("Não foi possível associar a tarefa a uma imobiliária.")
            tarefa = serializer.save(responsavel=self.request.user)


        if tarefa.responsavel and hasattr(tarefa.responsavel.perfil, 'google_calendar_token'):
            try:
                agendar_tarefa_no_calendario(tarefa)
            except Exception as e:
                print(f"Erro ao agendar tarefa no Google Calendar: {e}")
        
    def perform_update(self, serializer):
        if self.request.user.is_superuser or (serializer.instance.oportunidade.imobiliaria == self.request.tenant):
            tarefa = serializer.save()
            if tarefa.responsavel and hasattr(tarefa.responsavel.perfil, 'google_calendar_token'):
                try:
                    agendar_tarefa_no_calendario(tarefa, editar=True)
                except Exception as e:
                    print(f"Erro ao atualizar tarefa no Google Calendar: {e}")
        else:
            raise PermissionDenied("Você não tem permissão para atualizar esta tarefa.")


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
                queryset = queryset.filter(data_conclusao__date__gte=start_date, data_conclusao__date__lte=end_date)
        
        return queryset.order_by('data_conclusao')

class RelatoriosView(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request):
        if not request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN:
            raise PermissionDenied("Acesso não autorizado.")

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
        funil = Oportunidade.objects.filter(imobiliaria=tenant).values('status').annotate(total=Count('status'))
        return FunilVendasSerializer(funil, many=True).data

    def _get_origem_leads(self, tenant):
        origens = Cliente.objects.filter(imobiliaria=tenant).values('origem').annotate(total=Count('origem'))
        serializer = RelatorioOrigemSerializer(origens, many=True)
        return serializer.data

    def _get_desempenho_corretores(self, tenant):
        corretores_desempenho = PerfilUsuario.objects.filter(imobiliaria=tenant, cargo=PerfilUsuario.Cargo.CORRETOR).annotate(
            oportunidades_abertas=Count('oportunidades_responsavel', filter=Q(oportunidades_responsavel__status=Oportunidade.Status.ABERTO)),
            oportunidades_ganhas=Count('oportunidades_responsavel', filter=Q(oportunidades_responsavel__status=Oportunidade.Status.GANHO)),
            oportunidades_perdidas=Count('oportunidades_responsavel', filter=Q(oportunidades_responsavel__status=Oportunidade.Status.PERDIDO))
        )
        serializer = RelatorioCorretorSerializer(corretores_desempenho, many=True)
        return serializer.data

    def _get_relatorio_imobiliaria(self, tenant):
        hoje = localdate()
        primeiro_dia_mes = hoje.replace(day=1)
        
        oportunidades_mes = Oportunidade.objects.filter(
            imobiliaria=tenant,
            data_criacao__date__gte=primeiro_dia_mes
        )
        
        sumario = oportunidades_mes.aggregate(
            novas_oportunidades=Count('id'),
            oportunidades_ganhas=Count('id', filter=Q(status=Oportunidade.Status.GANHO)),
            oportunidades_perdidas=Count('id', filter=Q(status=Oportunidade.Status.PERDIDO))
        )
        
        oportunidades_por_mes = Oportunidade.objects.filter(imobiliaria=tenant, data_criacao__year=hoje.year)\
            .annotate(mes=TruncMonth('data_criacao'))\
            .values('mes')\
            .annotate(
                ganhas=Count('id', filter=Q(status=Oportunidade.Status.GANHO)),
                perdidas=Count('id', filter=Q(status=Oportunidade.Status.PERDIDO)),
                abertas=Count('id', filter=Q(status=Oportunidade.Status.ABERTO))
            )\
            .order_by('mes')

        dados = {
            'sumario_mes_atual': sumario,
            'oportunidades_por_mes': list(oportunidades_por_mes)
        }
        
        serializer = RelatorioImobiliariaSerializer(dados)
        return dados
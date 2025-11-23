# C:\wamp64\www\imobcloud\app_clientes\views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework import filters
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Count, Q
from django.utils.timezone import localdate
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from google_auth_oauthlib.flow import Flow
import os
import json
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Sum # Importação necessária para a soma

# Imports para PDF
from django.template.loader import render_to_string
from io import BytesIO
from xhtml2pdf import pisa
from datetime import date

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
)
from app_contratos.serializers import ClienteSimplificadoSerializer
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
    search_fields = ['nome', 'documento', 'razao_social', 'email', 'telefone']
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        base_queryset = Cliente.objects.filter(ativo=True)
        
        if self.request.user.is_superuser:
            queryset = base_queryset.all()
        elif self.request.tenant:
            queryset = base_queryset.filter(imobiliaria=self.request.tenant)
        else:
            return Cliente.objects.none()
            
        return queryset

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
        # CORREÇÃO: Verifica permissões booleanas
        elif hasattr(self.request.user, 'perfil') and (self.request.user.perfil.is_admin or self.request.user.perfil.is_corretor) and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar este cliente.")

    def perform_destroy(self, instance):
        # CORREÇÃO: Verifica permissões booleanas
        if self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and (self.request.user.perfil.is_admin or self.request.user.perfil.is_corretor) and instance.imobiliaria == self.request.tenant):
            instance.ativo = False
            instance.save()
        else:
            raise PermissionDenied("Você não tem permissão para inativar este cliente.")

    @action(detail=False, methods=['get'], url_path='lista-simples')
    def lista_simples(self, request):
        queryset = self.get_queryset() 
        serializer = ClienteSimplificadoSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='lista-proprietarios')
    def lista_proprietarios(self, request):
        base_queryset = self.get_queryset()
        finalidade = request.query_params.get('finalidade') 
        
        if not finalidade:
            return Response([], status=status.HTTP_400_BAD_REQUEST)
        
        queryset = base_queryset.filter(
            perfil_cliente__contains=['PROPRIETARIO'],
            imoveis_propriedade__status=finalidade 
        ).distinct() 
        
        serializer = ClienteSimplificadoSerializer(queryset, many=True)
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
        if self.request.user.is_superuser:
            return Visita.objects.all().prefetch_related('imoveis', 'cliente')
        elif self.request.tenant:
            return Visita.objects.filter(imobiliaria=self.request.tenant).prefetch_related('imoveis', 'cliente')
        return Visita.objects.none()

    def perform_create(self, serializer):
        cliente_id = self.request.data.get('cliente')
        cliente = get_object_or_404(Cliente, pk=cliente_id)
        
        imobiliaria = None
        if self.request.tenant:
            imobiliaria = self.request.tenant
        elif self.request.user.is_superuser:
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
            raise PermissionDenied("Não foi possível associar a visita. Tenant/Imobiliária não identificada.")

        # Salva o corretor responsável (quem criou a visita)
        serializer.save(imobiliaria=imobiliaria, cliente=cliente, corretor=self.request.user)

    def perform_update(self, serializer):
        # VALIDAÇÃO: Impede edição se já houver assinaturas (exceto updates internos de assinatura)
        instance = serializer.instance
        
        if (instance.assinatura_cliente or instance.assinatura_corretor):
             dados = self.request.data
             eh_processo_assinatura = 'assinatura_cliente' in dados or 'assinatura_corretor' in dados
             
             if not eh_processo_assinatura:
                 raise PermissionDenied("Não é possível editar os dados de uma visita que já possui assinaturas.")

        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar esta visita.")

    def perform_destroy(self, instance):
        # VALIDAÇÃO: Impede a exclusão se já houver assinaturas
        if instance.assinatura_cliente or instance.assinatura_corretor:
             raise PermissionDenied("Não é possível excluir uma visita que já foi assinada pelo cliente ou corretor.")

        if self.request.user.is_superuser:
            instance.delete()
        elif hasattr(self.request.user, 'perfil') and instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise PermissionDenied("Você não tem permissão para excluir esta visita.")


class AtividadeViewSet(viewsets.ModelViewSet):
    serializer_class = AtividadeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    queryset = Atividade.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-data_criacao')
        
        if self.request.tenant:
            queryset = queryset.filter(cliente__imobiliaria=self.request.tenant)

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
    queryset = Oportunidade.objects.all().select_related('cliente', 'imovel', 'responsavel')
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
        base_queryset = Oportunidade.objects.all()

        if user.is_superuser:
            queryset = base_queryset
        
        elif self.request.tenant:
            queryset = base_queryset.filter(imobiliaria=self.request.tenant)
            
            if hasattr(user, 'perfil') and not user.perfil.is_admin:
                queryset = queryset.filter(responsavel=user)
        
        else:
            return Oportunidade.objects.none()

        responsavel_id = self.request.query_params.get('responsavel')
        if responsavel_id:
            try:
                queryset = queryset.filter(responsavel__id=int(responsavel_id))
            except ValueError:
                pass 

        return queryset.order_by('data_criacao') 

    def perform_create(self, serializer):
        if not self.request.tenant:
            raise PermissionDenied("Apenas utilizadores associados a uma imobiliária podem criar oportunidades.")
        
        if not self.request.user.is_superuser and not hasattr(self.request.user, 'perfil'):
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

        oportunidade.refresh_from_db() 
        fase_nova_key = oportunidade.fase 
        
        if fase_nova_key != fase_anterior:
            fase_nova = oportunidade.get_fase_display()
            
            descricao = f"Oportunidade '{oportunidade.titulo}' movida da fase '{fase_anterior}' para '{fase_nova}'."
            
            Atividade.objects.create(
                cliente=oportunidade.cliente,
                tipo='MUDANCA_FASE',
                descricao=descricao,
                registrado_por=request.user
            )
        
        return response


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
        
        # Filtro por Oportunidade (importante para o form de edição)
        oportunidade_id = self.request.query_params.get('oportunidade')
        if oportunidade_id:
            queryset = queryset.filter(oportunidade_id=oportunidade_id)
            
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
                queryset = queryset.filter(data_vencimento__date__gte=start_date, data_vencimento__date__lte=end_date)
        
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
        elif relatorio_tipo == 'valor_estimado_aberto': # NOVO TIPO
            data = self._get_valor_estimado_aberto(tenant)
        else:
            return Response({"error": "Tipo de relatório inválido."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data)

    def _get_oportunidades_funil(self, tenant):
        funil = Oportunidade.objects.filter(imobiliaria=tenant).values('fase').annotate(total=Count('fase'))
        return list(funil)

    def _get_origem_leads(self, tenant):
        origens = Oportunidade.objects.filter(imobiliaria=tenant).values('fonte').annotate(total=Count('fonte'))
        return list(origens)

    def _get_desempenho_corretores(self, tenant):
        return {"message": "Relatório de desempenho de corretores a ser implementado."}
    
    def _get_relatorio_imobiliaria(self, tenant):
         return {"message": "Relatório de imobiliária a ser implementado."}
         
    # ====================================================================
    # NOVO: Valor Estimado de Leads em Aberto
    # ====================================================================
    def _get_valor_estimado_aberto(self, tenant):
        """Calcula a soma dos valores estimados para oportunidades que não são GANHO nem PERDIDO."""
        
        # Fases em aberto: LEAD, CONTATO, VISITA, PROPOSTA, NEGOCIACAO
        fases_abertas = [
            Oportunidade.Fases.LEAD, 
            Oportunidade.Fases.CONTATO, 
            Oportunidade.Fases.VISITA, 
            Oportunidade.Fases.PROPOSTA, 
            Oportunidade.Fases.NEGOCIACAO
        ]
        
        # Filtra por imobiliária E fase em aberto
        abertas_queryset = Oportunidade.objects.filter(
            imobiliaria=tenant,
            fase__in=fases_abertas
        )
        
        # Soma o valor estimado
        soma = abertas_queryset.aggregate(
            valor_total_aberto=Sum('valor_estimado')
        )
        
        # Retorna o resultado (usando 0 se for None)
        valor_total = soma['valor_total_aberto'] if soma['valor_total_aberto'] else 0.00
        
        return {
            "valor_total_aberto": valor_total
        }

# ====================================================================
# VIEW PARA GERAR PDF DA VISITA (Ficha de Visita)
# ====================================================================
class GerarRelatorioVisitaPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        # 1. Busca a visita
        if request.user.is_superuser:
            visita = get_object_or_404(Visita, pk=pk)
        elif request.tenant:
            visita = get_object_or_404(Visita, pk=pk, imobiliaria=request.tenant)
        else:
            return HttpResponse("Visita não encontrada ou acesso negado.", status=404)

        # 2. Prepara os dados
        imoveis = visita.imoveis.all()
        cliente = visita.cliente
        imobiliaria = visita.imobiliaria
        
        # Busca o corretor responsável pela visita, ou usa o usuário atual se antigo
        corretor = visita.corretor if visita.corretor else request.user
        
        hoje = timezone.now()

        context = {
            'visita': visita,
            'cliente': cliente,
            'imobiliaria': imobiliaria,
            'imoveis': imoveis,
            'data_impressao': hoje,
            'corretor': corretor, # Agora passa o corretor da visita
            'logo_url': None
        }

        # 3. Renderiza o HTML
        html_string = render_to_string('relatorio_visita_template.html', context)
        
        # 4. Gera o PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result, encoding='UTF-8')

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f'ficha_visita_{visita.id}_{cliente.nome.replace(" ", "_")}.pdf'
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        else:
            return HttpResponse(f"Erro ao gerar PDF: {pdf.err}", status=500)
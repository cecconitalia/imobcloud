from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q
from django.db import transaction

# --- Imports para CSRF Fix ---
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# -----------------------------

# --- Imports para Auto-Cadastro e Email ---
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.conf import settings
import traceback
import os
# ------------------------------------------

# Imports dos Apps (com tratamento de erro caso o app não esteja instalado)
try:
    from app_imoveis.models import Imovel
    from app_clientes.models import Cliente
    from app_contratos.models import Contrato, Pagamento
except ImportError:
    pass

from .models import PerfilUsuario, Imobiliaria, Notificacao, ConfiguracaoGlobal, Plano
from .serializers import (
    MyTokenObtainPairSerializer, 
    CorretorRegistrationSerializer, 
    CorretorDisplaySerializer,
    NotificacaoSerializer,
    ImobiliariaIntegracaoSerializer,
    ConfiguracaoGlobalSerializer,
    PublicRegisterSerializer,
    ImobiliariaSerializer,
    PerfilUsuarioSerializer,
    PlanoSerializer
)
from .permissions import IsAdminOrSuperUser, IsCorretorOrReadOnly

User = get_user_model()

# ==============================================================================
# AUTHENTICATION VIEWS
# ==============================================================================

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View de Login personalizada que força a permissão AllowAny.
    """
    permission_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# ==============================================================================
# VIEWSETS DE IMOBILIÁRIA E CONFIGURAÇÃO
# ==============================================================================

class ImobiliariaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar dados da Imobiliária (Tenant).
    Inclui suporte para upload de arquivos (Logo, Foto) e endpoint dedicado 'minha-imobiliaria'.
    """
    queryset = Imobiliaria.objects.all()
    serializer_class = ImobiliariaSerializer
    permission_classes = [IsAuthenticated]
    # Habilita suporte a upload de arquivos (multipart/form-data)
    parser_classes = (MultiPartParser, FormParser, JSONParser) 

    def get_queryset(self):
        # Retorna apenas a imobiliária do usuário logado (Tenant Isolation)
        user = self.request.user
        if hasattr(user, 'imobiliaria') and user.imobiliaria:
            return Imobiliaria.objects.filter(id=user.imobiliaria.id)
        if user.is_superuser:
            return Imobiliaria.objects.all()
        return Imobiliaria.objects.none()

    @action(detail=False, methods=['get', 'patch', 'put'], url_path='minha-imobiliaria')
    def minha_imobiliaria(self, request):
        """
        Endpoint simplificado para o frontend obter/atualizar 
        os dados da imobiliária do usuário logado.
        URL: /api/v1/core/imobiliarias/minha-imobiliaria/
        """
        try:
            # 1. Verifica vínculo
            if not hasattr(request.user, 'imobiliaria') or not request.user.imobiliaria:
                return Response(
                    {"detail": "Usuário não possui imobiliária vinculada."}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            imobiliaria = request.user.imobiliaria

            # 2. Retorna dados (GET)
            if request.method == 'GET':
                serializer = self.get_serializer(imobiliaria)
                return Response(serializer.data)

            # 3. Atualiza dados (PATCH/PUT)
            partial = request.method == 'PATCH'
            
            serializer = self.get_serializer(imobiliaria, data=request.data, partial=partial)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            traceback.print_exc()
            return Response(
                {"detail": f"Erro interno ao processar dados da imobiliária: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ConfiguracaoGlobalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna as configurações públicas do sistema (Logo do SaaS, Título, etc).
    """
    queryset = ConfiguracaoGlobal.objects.all()
    serializer_class = ConfiguracaoGlobalSerializer
    permission_classes = [AllowAny] 

    def list(self, request, *args, **kwargs):
        # Garante retornar sempre o primeiro registro (Singleton)
        config = ConfiguracaoGlobal.objects.first()
        if not config:
            return Response({})
        serializer = self.get_serializer(config)
        return Response(serializer.data)

class PlanoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plano.objects.filter(ativo=True)
    serializer_class = PlanoSerializer
    permission_classes = [permissions.AllowAny]

# ==============================================================================
# GESTÃO DE USUÁRIOS E NOTIFICAÇÕES
# ==============================================================================

class CorretorRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = CorretorRegistrationSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        if getattr(user, 'imobiliaria', None):
            return User.objects.filter(imobiliaria=user.imobiliaria)
        return User.objects.none()
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CorretorDisplaySerializer
        return CorretorRegistrationSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = CorretorDisplaySerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='minhas-notificacoes')
    def minhas_notificacoes(self, request):
        notificacoes = Notificacao.objects.filter(destinatario=request.user, lida=False).order_by('-data_criacao')
        serializer = NotificacaoSerializer(notificacoes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='marcar-notificacao-lida')
    def marcar_notificacao_lida(self, request, pk=None):
        try:
            notificacao = Notificacao.objects.get(pk=pk, destinatario=request.user)
            notificacao.lida = True
            notificacao.save()
            return Response({'status': 'ok'})
        except Notificacao.DoesNotExist:
            return Response({'error': 'Notificação não encontrada'}, status=404)

    @action(detail=False, methods=['get'])
    def lista_corretores_simples(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        data = [
            {
                'id': u.id, 
                'nome_completo': u.get_full_name() or u.username,
                'first_name': u.first_name,
                'email': u.email,
                'foto': u.foto_perfil.url if u.foto_perfil else None
            } 
            for u in queryset
        ]
        return Response(data)

class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    serializer_class = PerfilUsuarioSerializer 
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        if hasattr(user, 'imobiliaria') and user.imobiliaria:
            return User.objects.filter(imobiliaria=user.imobiliaria)
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Endpoint específico para manipular o próprio usuário logado.
        Permite atualizar perfil, senha e foto.
        """
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(user, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def perform_create(self, serializer):
        if self.request.user.imobiliaria:
            serializer.save(imobiliaria=self.request.user.imobiliaria)
        else:
            serializer.save()

# ==============================================================================
# NOTIFICAÇÕES (ViewSet Completo)
# ==============================================================================

class NotificacaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para notificações.
    Permite listar, criar e marcar como lida.
    """
    serializer_class = NotificacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notificacao.objects.filter(destinatario=self.request.user).order_by('-data_criacao')

    @action(detail=False, methods=['post'], url_path='marcar-todas-lidas')
    def marcar_todas_lidas(self, request):
        self.get_queryset().filter(lida=False).update(lida=True)
        return Response(status=status.HTTP_200_OK)

# ==============================================================================
# DASHBOARD E STATS
# ==============================================================================

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Estrutura completa esperada pelo Frontend
        data = {
            'oportunidades_ativas': 0,
            'tarefas_pendentes': 0,
            'receita_mes': 0,
            'imoveis_ativos': 0,
            'financeiro_previsto_entrada': 0,
            'financeiro_previsto_saida': 0,
            'tarefas_hoje': [],
            'funil_resumo': [],
            'proximas_visitas': [],
            'total_oportunidades': 0
        }

        try:
            print("--- INICIANDO CARGA DO DASHBOARD ---") # Debug
            user = request.user
            imobiliaria = getattr(request, 'tenant', None)
            
            # Fallback para encontrar a imobiliária
            if not imobiliaria and hasattr(user, 'imobiliaria') and user.imobiliaria:
                imobiliaria = user.imobiliaria

            # Se não encontrar imobiliária e não for superuser, retorna zerado
            if not imobiliaria and not user.is_superuser:
                print("--- SEM IMOBILIÁRIA VINCULADA ---")
                return Response(data)

            print(f"Imobiliária Ativa: {imobiliaria} (ID: {imobiliaria.id})") # Debug

            hoje = timezone.now().date()
            inicio_mes = hoje.replace(day=1)
            
            # --- 1. IMÓVEIS ---
            try:
                from app_imoveis.models import Imovel
                qs_imoveis = Imovel.objects.all()
                if imobiliaria:
                    qs_imoveis = qs_imoveis.filter(imobiliaria=imobiliaria)
                
                data['imoveis_ativos'] = qs_imoveis.exclude(status='DESATIVADO').count()
                print(f"Imóveis: {data['imoveis_ativos']}") # Debug
            except Exception as e:
                print(f"Erro Imóveis: {e}")

            # --- 2. CLIENTES, OPORTUNIDADES E FUNIL ---
            try:
                from app_clientes.models import Oportunidade, Tarefa, Visita
                
                # --- OPORTUNIDADES ---
                qs_ops = Oportunidade.objects.all()
                if imobiliaria:
                    qs_ops = qs_ops.filter(imobiliaria=imobiliaria)
                
                # Debug: Total bruto antes de filtrar
                print(f"Total Bruto Oportunidades: {qs_ops.count()}")

                # KPI: Oportunidades Ativas
                # Removemos 'GANHO', 'PERDIDO', 'ganho', 'perdido' para garantir
                ops_ativas = qs_ops.exclude(fase__in=['GANHO', 'PERDIDO', 'ganho', 'perdido', 'Ganho', 'Perdido'])
                data['oportunidades_ativas'] = ops_ativas.count()
                data['total_oportunidades'] = ops_ativas.count()
                
                print(f"Oportunidades Ativas: {data['oportunidades_ativas']}") # Debug

                # Gráfico: Resumo do Funil
                funil_data = ops_ativas.values('fase').annotate(total=Count('id')).order_by('fase')
                
                fase_labels = {
                    'LEAD': 'Leads',
                    'QUALIFICACAO': 'Qualificação',
                    'VISITA': 'Visita',
                    'PROPOSTA': 'Proposta',
                    'NEGOCIACAO': 'Negociação'
                }
                
                funil_resumo = []
                for item in funil_data:
                    fase_cod = item['fase']
                    # Adiciona mesmo se não tiver label, para debug
                    titulo = fase_labels.get(fase_cod, fase_cod)
                    funil_resumo.append({'titulo': titulo, 'total': item['total']})
                
                data['funil_resumo'] = funil_resumo

                # --- TAREFAS ---
                # Filtro inicial: Status Pendente
                qs_tarefas = Tarefa.objects.filter(status='PENDENTE')
                
                if imobiliaria:
                    # CORREÇÃO: Filtra tarefas onde o cliente pertence à imob OU o responsável pertence à imob
                    # Isso pega tarefas internas que não têm cliente vinculado
                    qs_tarefas = qs_tarefas.filter(
                        Q(cliente__imobiliaria=imobiliaria) | 
                        Q(responsavel__imobiliaria=imobiliaria)
                    ).distinct()

                # Se for corretor (não admin), vê apenas as suas
                if not user.is_superuser and not user.is_admin:
                    qs_tarefas = qs_tarefas.filter(responsavel=user)
                
                data['tarefas_pendentes'] = qs_tarefas.count()
                print(f"Tarefas Pendentes: {data['tarefas_pendentes']}") # Debug

                # Lista: Tarefas de Hoje
                tarefas_hoje = qs_tarefas.filter(data_vencimento__date=hoje).order_by('data_vencimento')[:5]
                data['tarefas_hoje'] = [
                    {
                        'id': t.id,
                        'titulo': t.titulo,
                        'data_vencimento': t.data_vencimento,
                        'cliente_nome': str(t.cliente) if t.cliente else "Interno"
                    } for t in tarefas_hoje
                ]

                # --- VISITAS ---
                qs_visitas = Visita.objects.filter(data__gte=timezone.now(), status='AGENDADA')
                if imobiliaria:
                    # Tenta filtrar por cliente da imobiliária ou imóvel da imobiliária
                    qs_visitas = qs_visitas.filter(
                        Q(cliente__imobiliaria=imobiliaria) | 
                        Q(imovel__imobiliaria=imobiliaria)
                    ).distinct()

                if not user.is_superuser and not user.is_admin:
                     qs_visitas = qs_visitas.filter(corretor=user)
                
                visitas_prox = qs_visitas.order_by('data')[:5]
                data['proximas_visitas'] = [
                    {
                        'id': v.id,
                        'data': v.data,
                        # Verifica relacionamentos com segurança (ManyMany ou ForeignKey)
                        'imovel_titulo': str(v.imoveis.first()) if hasattr(v, 'imoveis') and v.imoveis.exists() else (str(v.imovel) if hasattr(v, 'imovel') and v.imovel else "Não informado"),
                        'imovel_id': v.imoveis.first().id if hasattr(v, 'imoveis') and v.imoveis.exists() else (v.imovel.id if hasattr(v, 'imovel') and v.imovel else 0),
                        'cliente_nome': str(v.cliente) if v.cliente else 'Cliente'
                    } for v in visitas_prox
                ]

            except Exception as e:
                print(f"Erro App Clientes: {e}")
                traceback.print_exc()
            
            # --- 3. FINANCEIRO ---
            try:
                from app_financeiro.models import Transacao
                
                qs_fin = Transacao.objects.all()
                if imobiliaria:
                    qs_fin = qs_fin.filter(imobiliaria=imobiliaria)

                # Receita do Mês
                receita = qs_fin.filter(
                    tipo='RECEITA', 
                    status='PAGO', 
                    data_pagamento__gte=inicio_mes
                ).aggregate(Sum('valor'))['valor__sum']
                data['receita_mes'] = receita if receita else 0

                # Previsões
                entradas_prev = qs_fin.filter(
                    tipo='RECEITA',
                    status='PENDENTE',
                    data_vencimento__gte=inicio_mes,
                    data_vencimento__month=hoje.month
                ).aggregate(Sum('valor'))['valor__sum']
                data['financeiro_previsto_entrada'] = entradas_prev if entradas_prev else 0

                saidas_prev = qs_fin.filter(
                    tipo='DESPESA',
                    status='PENDENTE',
                    data_vencimento__gte=inicio_mes,
                    data_vencimento__month=hoje.month
                ).aggregate(Sum('valor'))['valor__sum']
                data['financeiro_previsto_saida'] = saidas_prev if saidas_prev else 0
                
                print(f"Receita Mês: {data['receita_mes']}") # Debug

            except ImportError:
                pass
            except Exception as e:
                print(f"Erro Financeiro: {e}")

            print("--- DASHBOARD FINALIZADO COM SUCESSO ---")
            return Response(data)

        except Exception as e:
            traceback.print_exc()
            return Response(data)
    
class IntegracaoRedesSociaisView(APIView):
    """
    View específica para salvar chaves de integração via POST/PUT.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ImobiliariaIntegracaoSerializer

    def get(self, request, *args, **kwargs):
        imobiliaria = request.user.imobiliaria
        if not imobiliaria:
             return Response({"error": "Imobiliária não encontrada."}, status=404)
             
        if not (request.user.is_superuser or request.user.is_admin):
            return Response({"error": "Acesso não autorizado."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.serializer_class(imobiliaria)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        imobiliaria = request.user.imobiliaria
        if not imobiliaria:
             return Response({"error": "Imobiliária não encontrada."}, status=404)

        if not (request.user.is_superuser or request.user.is_admin):
            return Response({"error": "Acesso não autorizado."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.serializer_class(imobiliaria, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Credenciais salvas com sucesso!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==============================================================================
# VIEWS MANUAIS DE NOTIFICAÇÃO (Mantidas para compatibilidade)
# ==============================================================================

class MinhasNotificacoesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notificacoes = Notificacao.objects.filter(destinatario=request.user, lida=False)
        serializer = NotificacaoSerializer(notificacoes, many=True)
        return Response(serializer.data)

class MarcarNotificacaoLidaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notificacao = Notificacao.objects.get(pk=pk, destinatario=request.user)
            notificacao.lida = True
            notificacao.save()
            return Response({'status': 'ok'})
        except Notificacao.DoesNotExist:
            return Response({'error': 'Notificação não encontrada'}, status=404)

# ==============================================================================
# CADASTRO PÚBLICO COM GARANTIA DE TRANSAÇÃO (ATOMIC)
# ==============================================================================
@method_decorator(csrf_exempt, name='dispatch')
class PublicRegisterView(APIView):
    """
    View de cadastro público (SaaS).
    Cria a Imobiliária, o Subdomínio e o Usuário Admin em uma única transação.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        nome_completo = data.get('nome')
        email = data.get('email')
        nome_imobiliaria = data.get('nome_imobiliaria')
        telefone = data.get('telefone')

        if not all([nome_completo, email, nome_imobiliaria]):
            return Response({"error": "Preencha todos os campos obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Este email já está cadastrado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # O bloco 'atomic' garante que se a criação do usuário falhar, 
            # a imobiliária também não será salva, evitando dados órfãos.
            with transaction.atomic():
                # 1. Gera subdomínio único
                base_subdomain = slugify(nome_imobiliaria).replace('-', '')
                if not base_subdomain: base_subdomain = "nova"
                subdomain = base_subdomain
                counter = 1
                while Imobiliaria.objects.filter(subdominio=subdomain).exists():
                    subdomain = f"{base_subdomain}{counter}"
                    counter += 1

                # 2. Cria a imobiliária
                imobiliaria = Imobiliaria.objects.create(
                    nome_fantasia=nome_imobiliaria, # Usando nome_fantasia conforme model
                    razao_social=nome_imobiliaria,
                    subdominio=subdomain,
                    email_contato=email,
                    telefone=telefone,
                    status_financeiro='GRATIS'
                )

                # 3. Gera senha e prepara dados do usuário
                senha_gerada = get_random_string(length=10)
                partes_nome = nome_completo.strip().split(" ")
                first_name = partes_nome[0]
                last_name = " ".join(partes_nome[1:]) if len(partes_nome) > 1 else ""
                
                # 4. Cria o usuário vinculado à imobiliária
                user = User.objects.create_user(
                    username=email, 
                    email=email, 
                    password=senha_gerada,
                    first_name=first_name,
                    last_name=last_name,
                    telefone=telefone,
                    imobiliaria=imobiliaria,
                    is_admin=True,
                    is_corretor=True
                )

            # --- ENVIO DE EMAIL (Fora do bloco atomic para evitar gargalo no banco) ---
            mensagem_extra = "Verifique seu e-mail para pegar a senha."
            credenciais_temp = {} 

            try:
                remetente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@imobhome.com.br')
                assunto = "Bem-vindo ao ImobHome - Suas Credenciais"
                msg_corpo = f"""
Olá {first_name},

Sua conta no ImobHome foi criada com sucesso!

Aqui estão seus dados de acesso:
-----------------------------------
Link: https://imobhome.com.br/login
Usuário: {email}
Senha: {senha_gerada}
-----------------------------------

Seu subdomínio: {subdomain}.imobhome.com.br
                """
                send_mail(assunto, msg_corpo, remetente, [email], fail_silently=False)
            except Exception as mail_error:
                print(f"AVISO EMAIL: {mail_error}")
                mensagem_extra = "Não foi possível enviar o e-mail. Anote sua senha abaixo."
                credenciais_temp = {"senha_gerada": senha_gerada}

            return Response({
                "message": f"Cadastro realizado! {mensagem_extra}",
                "email": email,
                "subdominio": subdomain,
                **credenciais_temp
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            traceback.print_exc()
            return Response({"error": f"Erro interno ao gravar dados: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConfiguracaoGlobalView(APIView):
    # View legada (mantida para evitar quebra, mas o ViewSet é preferível)
    permission_classes = [IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Acesso restrito."}, status=status.HTTP_403_FORBIDDEN)

        config, created = ConfiguracaoGlobal.objects.get_or_create(pk=1)
        serializer = ConfiguracaoGlobalSerializer(config)
        return Response(serializer.data)

    def put(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Acesso restrito."}, status=status.HTTP_403_FORBIDDEN)

        config, created = ConfiguracaoGlobal.objects.get_or_create(pk=1)
        serializer = ConfiguracaoGlobalSerializer(config, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
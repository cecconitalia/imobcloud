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
from django.db import transaction  # Importante para atomicidade

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

from .models import PerfilUsuario, Imobiliaria, Notificacao, ConfiguracaoGlobal
from .serializers import (
    MyTokenObtainPairSerializer, 
    CorretorRegistrationSerializer, 
    CorretorDisplaySerializer,
    NotificacaoSerializer,
    ImobiliariaIntegracaoSerializer,
    ConfiguracaoGlobalSerializer,
    PublicRegisterSerializer,
    ImobiliariaSerializer, # Novo serializer completo
    PerfilUsuarioSerializer
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
    ViewSet para gerenciar dados da Imobiliária.
    Inclui suporte para upload de arquivos (Logo).
    """
    queryset = Imobiliaria.objects.all()
    serializer_class = ImobiliariaSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser) 

    def get_queryset(self):
        # Retorna apenas a imobiliária do usuário logado (Tenant Isolation)
        user = self.request.user
        if hasattr(user, 'imobiliaria') and user.imobiliaria:
            return Imobiliaria.objects.filter(id=user.imobiliaria.id)
        if user.is_superuser:
            return Imobiliaria.objects.all()
        return Imobiliaria.objects.none()

    @action(detail=False, methods=['get', 'patch', 'put'])
    def me(self, request):
        """
        Retorna ou atualiza a imobiliária do usuário logado.
        Endpoint: /api/v1/core/imobiliarias/me/
        """
        # Verifica se o usuário tem imobiliária vinculada
        if not hasattr(request.user, 'imobiliaria') or not request.user.imobiliaria:
            return Response(
                {"detail": "Usuário não possui imobiliária vinculada."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        imobiliaria = request.user.imobiliaria

        if request.method == 'GET':
            serializer = self.get_serializer(imobiliaria)
            return Response(serializer.data)

        elif request.method in ['PATCH', 'PUT']:
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(imobiliaria, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class ConfiguracaoGlobalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna as configurações públicas do sistema (Logo, Título, etc).
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
# DASHBOARD E STATS
# ==============================================================================

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            user = request.user
            imobiliaria = getattr(request, 'tenant', None)
            
            # Fallback para encontrar a imobiliária
            if not imobiliaria and hasattr(user, 'imobiliaria') and user.imobiliaria:
                imobiliaria = user.imobiliaria

            # Fallback final (não recomendado em prod, mas útil para testes locais)
            if not imobiliaria and not user.is_superuser:
                # Tenta pegar pelo subdomínio padrão
                imobiliaria = Imobiliaria.objects.filter(subdominio='imobhome').first()

            if not imobiliaria and not user.is_superuser:
                return Response({
                    'total_imoveis': 0, 'total_clientes': 0,
                    'total_contratos_ativos': 0, 'total_a_receber_30d': 0,
                })

            filter_kwargs = {}
            if imobiliaria:
                filter_kwargs['imobiliaria'] = imobiliaria
            
            # Contagem de Imóveis
            try:
                total_imoveis = Imovel.objects.filter(**filter_kwargs).exclude(status='DESATIVADO').count()
            except Exception: 
                total_imoveis = 0
            
            # Contagem de Clientes
            try:
                total_clientes = Cliente.objects.filter(**filter_kwargs).count()
            except Exception: 
                total_clientes = 0
            
            # Contratos Ativos
            try:
                total_contratos_ativos = Contrato.objects.filter(
                    imobiliaria=imobiliaria, 
                    status_contrato='ATIVO'
                ).count()
            except Exception: 
                total_contratos_ativos = 0
            
            # Financeiro a Receber (Próximos 30 dias)
            total_a_receber = 0
            try:
                hoje = timezone.now().date()
                trinta_dias = hoje + timedelta(days=30)
                
                if imobiliaria:
                    pagamentos_qs = Pagamento.objects.filter(
                        contrato__imobiliaria=imobiliaria,
                        status='PENDENTE',
                        data_vencimento__gte=hoje, 
                        data_vencimento__lte=trinta_dias
                    )
                    soma = pagamentos_qs.aggregate(Sum('valor'))['valor__sum']
                    total_a_receber = soma if soma else 0
            except Exception:
                total_a_receber = 0

            return Response({
                'total_imoveis': total_imoveis,
                'total_clientes': total_clientes,
                'total_contratos_ativos': total_contratos_ativos,
                'total_a_receber_30d': total_a_receber,
            })

        except Exception as e:
            traceback.print_exc()
            return Response({
                'total_imoveis': 0, 'total_clientes': 0,
                'total_contratos_ativos': 0, 'total_a_receber_30d': 0,
                'error': str(e)
            })
    
class IntegracaoRedesSociaisView(APIView):
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
# NOTIFICAÇÕES (Views Adicionais)
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
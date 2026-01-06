# C:\wamp64\www\ImobCloud\core\views.py

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, permissions 
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q

# --- Imports para Auto-Cadastro e Email ---
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.conf import settings
import traceback
import os
# ------------------------------------------

from rest_framework_simplejwt.tokens import RefreshToken

from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from app_contratos.models import Contrato, Pagamento

from .models import PerfilUsuario, Imobiliaria, Notificacao
from .serializers import (
    MyTokenObtainPairSerializer, 
    CorretorRegistrationSerializer, 
    CorretorDisplaySerializer,
    NotificacaoSerializer,
    ImobiliariaIntegracaoSerializer
)
from rest_framework.decorators import action
from .permissions import IsAdminOrSuperUser, IsCorretorOrReadOnly

User = get_user_model()

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View de Login personalizada que força a permissão AllowAny.
    Isso é necessário porque o settings.py bloqueia tudo por padrão (IsSubscriptionActive),
    então precisamos abrir uma exceção explícita para a tela de login.
    """
    permission_classes = [AllowAny] # Permite acesso sem token e sem checagem financeira
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

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            user = request.user
            imobiliaria = getattr(request, 'tenant', None)
            
            # --- LÓGICA CORRIGIDA DE DETECÇÃO DE IMOBILIÁRIA ---
            
            # 1. Tenta pegar do usuário direto
            if not imobiliaria and hasattr(user, 'imobiliaria') and user.imobiliaria:
                imobiliaria = user.imobiliaria

            # 2. Tenta pegar do PERFIL do usuário (Igual ao app_contratos)
            if not imobiliaria and hasattr(user, 'perfil') and user.perfil:
                imobiliaria = user.perfil.imobiliaria

            # 3. Fallback para Localhost (Força 'imobhome')
            if not imobiliaria:
                imobiliaria = Imobiliaria.objects.filter(subdominio='imobhome').first()
                # 4. Último recurso: pega a primeira do banco
                if not imobiliaria:
                    imobiliaria = Imobiliaria.objects.first()

            # ==================================================================
            # DEBUG
            print(f"\n--- DEBUG DASHBOARD CORE ---")
            if imobiliaria:
                print(f"Imobiliária Definida: {imobiliaria.nome} (ID: {imobiliaria.id})")
            else:
                print("ERRO: Nenhuma imobiliária encontrada.")
            # ==================================================================

            # Se mesmo assim não achar, retorna zerado (mas não deve acontecer com o fallback acima)
            if not imobiliaria and not user.is_superuser:
                return Response({
                    'total_imoveis': 0, 'total_clientes': 0,
                    'total_contratos_ativos': 0, 'total_a_receber_30d': 0,
                })

            filter_kwargs = {}
            if imobiliaria:
                filter_kwargs['imobiliaria'] = imobiliaria
            
            # --- 1. IMÓVEIS ---
            try:
                # Exclui DESATIVADO e VENDIDO (opcional, dependendo da regra de negócio)
                total_imoveis = Imovel.objects.filter(**filter_kwargs).exclude(status='DESATIVADO').count()
            except Exception as e: 
                print(f"Erro contagem Imóveis: {e}")
                total_imoveis = 0
            
            # --- 2. CLIENTES ---
            try:
                total_clientes = Cliente.objects.filter(**filter_kwargs).count()
            except Exception: 
                total_clientes = 0
            
            # --- 3. CONTRATOS ---
            try:
                # Tenta filtrar diretamente pela imobiliária
                total_contratos_ativos = Contrato.objects.filter(
                    imobiliaria=imobiliaria, 
                    status_contrato='ATIVO'
                ).count()
            except Exception as e: 
                print(f"Erro contagem Contratos: {e}")
                total_contratos_ativos = 0
            
            # --- 4. FINANCEIRO (A Receber 30 dias) ---
            total_a_receber = 0
            try:
                hoje = timezone.now().date()
                trinta_dias = hoje + timedelta(days=30)
                
                if imobiliaria:
                    # Filtra pagamentos pendentes de contratos ATIVOS dessa imobiliária
                    pagamentos_qs = Pagamento.objects.filter(
                        contrato__imobiliaria=imobiliaria,
                        status='PENDENTE',
                        data_vencimento__gte=hoje, 
                        data_vencimento__lte=trinta_dias
                    )
                    soma = pagamentos_qs.aggregate(Sum('valor'))['valor__sum']
                    total_a_receber = soma if soma else 0
            except Exception as e:
                print(f"Erro Financeiro Dashboard: {e}")
                total_a_receber = 0

            return Response({
                'total_imoveis': total_imoveis,
                'total_clientes': total_clientes,
                'total_contratos_ativos': total_contratos_ativos,
                'total_a_receber_30d': total_a_receber,
            })

        except Exception as e:
            print(f"ERRO CRÍTICO DASHBOARD: {e}")
            traceback.print_exc()
            return Response({
                'total_imoveis': 0, 'total_clientes': 0,
                'total_contratos_ativos': 0, 'total_a_receber_30d': 0,
            })
    
class IntegracaoRedesSociaisView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ImobiliariaIntegracaoSerializer

    def get(self, request, *args, **kwargs):
        imobiliaria = request.tenant
        if not (request.user.is_superuser or request.user.is_admin):
            return Response({"error": "Acesso não autorizado."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(imobiliaria)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        imobiliaria = request.tenant
        if not (request.user.is_superuser or request.user.is_admin):
            return Response({"error": "Acesso não autorizado."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(imobiliaria, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Credenciais salvas com sucesso!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar perfis de usuários.
    """
    serializer_class = CorretorDisplaySerializer # ou PerfilUsuarioSerializer dependendo do uso
    # Usa as permissões padrão do settings.py (IsAuthenticated + IsSubscriptionActive)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        # Usuário comum vê apenas a si mesmo e colegas da mesma imobiliária
        if hasattr(user, 'imobiliaria') and user.imobiliaria:
            return User.objects.filter(imobiliaria=user.imobiliaria)
        return User.objects.filter(id=user.id)

    def get_object(self):
        # Permite retornar o usuário logado com a rota /me/
        pk = self.kwargs.get('pk')
        if pk == 'me':
            return self.request.user
        return super().get_object()

    def perform_create(self, serializer):
        # Garante que o usuário criado pertença à mesma imobiliária de quem cria
        if self.request.user.imobiliaria:
            serializer.save(imobiliaria=self.request.user.imobiliaria)
        else:
            serializer.save()

class MinhasNotificacoesView(APIView):
    """
    Retorna as notificações não lidas do usuário logado.
    """
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
# NOVA VIEW: AUTO-CADASTRO PÚBLICO COM ENVIO DE EMAIL
# ==============================================================================
class PublicRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            nome_completo = data.get('nome')
            email = data.get('email')
            nome_imobiliaria = data.get('nome_imobiliaria')
            telefone = data.get('telefone')

            if not all([nome_completo, email, nome_imobiliaria]):
                return Response({"error": "Preencha todos os campos obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email).exists():
                return Response({"error": "Este email já está cadastrado."}, status=status.HTTP_400_BAD_REQUEST)

            # 1. Gerar Subdomínio
            base_subdomain = slugify(nome_imobiliaria).replace('-', '')
            if not base_subdomain: base_subdomain = "nova"
            subdomain = base_subdomain
            counter = 1
            while Imobiliaria.objects.filter(subdominio=subdomain).exists():
                subdomain = f"{base_subdomain}{counter}"
                counter += 1

            # 2. Criar Imobiliária
            imobiliaria = Imobiliaria.objects.create(
                nome=nome_imobiliaria, 
                subdominio=subdomain,
                email_contato=email,
                telefone=telefone
            )

            # 3. Criar Usuário e Senha
            senha_gerada = get_random_string(length=10)
            partes_nome = nome_completo.strip().split(" ")
            first_name = partes_nome[0]
            last_name = " ".join(partes_nome[1:]) if len(partes_nome) > 1 else ""
            
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

            # 4. Enviar Email de Boas-Vindas
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
                Link: http://localhost:5173/login
                Usuário: {email}
                Senha: {senha_gerada}
                -----------------------------------
                
                Seu subdomínio: {subdomain}.imobhome.com.br
                """
                send_mail(assunto, msg_corpo, remetente, [email], fail_silently=False)
            except Exception as mail_error:
                print(f"AVISO EMAIL: {mail_error}")
                # Se o email falhar (ex: sem internet ou config), mostra a senha na tela
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
            return Response({"error": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
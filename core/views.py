# C:\wamp64\www\ImobCloud\core\views.py

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Sum

# --- NOVAS IMPORTAÇÕES PARA LOGOUT ---
from rest_framework_simplejwt.tokens import RefreshToken

# Importações dos modelos de outros apps
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from app_contratos.models import Contrato, Pagamento

# Importações locais do app 'core'
from .models import PerfilUsuario, Imobiliaria, Notificacao
from .serializers import (
    MyTokenObtainPairSerializer, 
    CorretorRegistrationSerializer, 
    CorretorDisplaySerializer,
    NotificacaoSerializer,
    ImobiliariaIntegracaoSerializer
)
# Importação do 'action'
from rest_framework.decorators import action


User = get_user_model()

class MyTokenObtainPairView(TokenObtainPairView):
    """
    View existente para o login, que já adiciona o subdomínio e o cargo à resposta.
    Permanece sem alterações.
    """
    serializer_class = MyTokenObtainPairSerializer

# --- NOVA VIEW DE LOGOUT ADICIONADA ---
class LogoutView(APIView):
    """
    Endpoint para fazer logout do utilizador.
    Adiciona o refresh token a uma blacklist para invalidá-lo.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
# --- FIM DA VIEW DE LOGOUT ---


class DashboardStatsView(APIView):
    """
    Esta view calcula e retorna estatísticas chave para o dashboard
    da imobiliária autenticada.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tenant = request.tenant

        if not tenant and request.user.is_superuser:
            try:
                tenant = Imobiliaria.objects.first()
                if not tenant:
                    return Response({"error": "Nenhuma imobiliária cadastrada no sistema."}, status=404)
            except Imobiliaria.DoesNotExist:
                return Response({"error": "Nenhuma imobiliária cadastrada no sistema."}, status=404)
        
        if not tenant:
            return Response({"error": "Nenhuma imobiliária selecionada."}, status=400)

        imoveis_ativos = Imovel.objects.filter(
            imobiliaria=tenant
        ).exclude(
            status__in=['Vendido', 'Desativado']
        ).count()

        clientes_ativos = Cliente.objects.filter(
            imobiliaria=tenant,
            ativo=True
        ).count()

        contratos_ativos = Contrato.objects.filter(
            imobiliaria=tenant,
            status_contrato='Ativo'
        ).count()
        
        trinta_dias_atras = timezone.now() - timedelta(days=30)
        novos_clientes = Cliente.objects.filter(
            imobiliaria=tenant,
            data_cadastro__gte=trinta_dias_atras
        ).count()
        
        faturamento_30d = Pagamento.objects.filter(
            contrato__imobiliaria=tenant,
            status='PAGO',
            data_pagamento__gte=trinta_dias_atras
        ).aggregate(total=Sum('valor'))['total'] or 0

        pagamentos_pendentes = Pagamento.objects.filter(
            contrato__imobiliaria=tenant,
            status__in=['PENDENTE', 'ATRASADO']
        ).aggregate(total=Sum('valor'))['total'] or 0

        total_vendas_ativas = Contrato.objects.filter(
            imobiliaria=tenant,
            status_contrato='Ativo',
            tipo_contrato='Venda'
        ).aggregate(total=Sum('valor_total'))['total'] or 0

        data = {
            'imoveis_ativos': imoveis_ativos,
            'clientes_ativos': clientes_ativos,
            'contratos_ativos': contratos_ativos,
            'novos_clientes_30d': novos_clientes,
            'faturamento_30d': faturamento_30d,
            'pagamentos_pendentes': pagamentos_pendentes,
            'total_vendas_ativas': total_vendas_ativas,
        }
        
        return Response(data)

# VIEWSET DEDICADA PARA NOTIFICAÇÕES
class NotificacaoViewSet(viewsets.GenericViewSet):
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='marcar-como-lida')
    def marcar_como_lida(self, request, pk=None):
        try:
            notificacao = self.get_queryset().get(pk=pk, destinatario=request.user)
            notificacao.lida = True
            notificacao.save()
            return Response({'status': 'Notificação marcada como lida'}, status=status.HTTP_200_OK)
        except Notificacao.DoesNotExist:
            return Response({'error': 'Notificação não encontrada ou não pertence a você.'}, status=status.HTTP_404_NOT_FOUND)


class CorretorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        
        if self.request.tenant:
            perfis = PerfilUsuario.objects.filter(imobiliaria=self.request.tenant)
            return User.objects.filter(perfil__in=perfis)

        return User.objects.none()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CorretorRegistrationSerializer
        return CorretorDisplaySerializer

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'perfil') or self.request.user.perfil.cargo != PerfilUsuario.Cargo.ADMIN:
            raise PermissionError("Apenas administradores podem registar novos utilizadores.")

        serializer.save(imobiliaria=self.request.tenant)

    def perform_update(self, serializer):
        instance = self.get_object()
        user_perfil = instance.perfil

        if self.request.user.is_superuser:
            pass
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and user_perfil.imobiliaria == self.request.tenant:
            pass
        else:
            raise PermissionError("Você não tem permissão para editar este utilizador.")

        serializer.save(imobiliaria=self.request.tenant)

    @action(detail=False, methods=['get'], url_path='minhas-notificacoes')
    def minhas_notificacoes(self, request):
        notificacoes = Notificacao.objects.filter(destinatario=request.user, lida=False)
        serializer = NotificacaoSerializer(notificacoes, many=True)
        return Response(serializer.data)
    
class IntegracaoRedesSociaisView(APIView):
    """
    View para a imobiliária (tenant) gerir as suas credenciais
    de integração com Facebook e Instagram.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ImobiliariaIntegracaoSerializer

    def get(self, request, *args, **kwargs):
        imobiliaria = request.tenant
        # Apenas o admin da imobiliária ou o superusuário podem ver as credenciais
        if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.cargo == 'ADMIN')):
            return Response({"error": "Acesso não autorizado."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.serializer_class(imobiliaria)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        imobiliaria = request.tenant
        # Apenas o admin da imobiliária ou o superusuário podem atualizar as credenciais
        if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.cargo == 'ADMIN')):
            return Response({"error": "Acesso não autorizado."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(imobiliaria, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Credenciais salvas com sucesso!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
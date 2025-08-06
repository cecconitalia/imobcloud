# C:\wamp64\www\ImobCloud\core\views.py

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets
from .serializers import MyTokenObtainPairSerializer, CorretorRegistrationSerializer, CorretorDisplaySerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from app_contratos.models import Contrato
from core.models import PerfilUsuario

User = get_user_model()

class MyTokenObtainPairView(TokenObtainPairView):
    """
    View existente para o login, que já adiciona o subdomínio e o cargo à resposta.
    Permanece sem alterações.
    """
    serializer_class = MyTokenObtainPairSerializer


class DashboardStatsView(APIView):
    """
    Esta view calcula e retorna estatísticas chave para o dashboard
    da imobiliária autenticada.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tenant = request.tenant

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

        data = {
            'imoveis_ativos': imoveis_ativos,
            'clientes_ativos': clientes_ativos,
            'contratos_ativos': contratos_ativos,
            'novos_clientes_30d': novos_clientes,
        }
        
        return Response(data)

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

        # O serializer agora lida com a lógica de criação do perfil
        serializer.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        user_perfil = instance.perfil

        if self.request.user.is_superuser:
            pass
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and user_perfil.imobiliaria == self.request.tenant:
            pass
        else:
            raise PermissionError("Você não tem permissão para editar este utilizador.")

        # O serializer agora lida com a lógica de atualização do perfil
        serializer.save()
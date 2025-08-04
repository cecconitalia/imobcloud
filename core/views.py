from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from app_contratos.models import Contrato


class MyTokenObtainPairView(TokenObtainPairView):
    """
    View existente para o login, permanece sem alterações.
    """
    serializer_class = MyTokenObtainPairSerializer


class DashboardStatsView(APIView):
    """
    Esta view calcula e retorna estatísticas chave para o dashboard
    da imobiliária autenticada.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # A lógica para obter o tenant (imobiliária) é tratada pelo middleware
        tenant = request.tenant

        if not tenant:
            # Se não houver um tenant (ex: superuser no domínio principal),
            # retorna uma mensagem de erro.
            return Response({"error": "Nenhuma imobiliária selecionada."}, status=400)

        # 1. Contar imóveis ativos (não vendidos ou desativados)
        imoveis_ativos = Imovel.objects.filter(
            imobiliaria=tenant
        ).exclude(
            status__in=['Vendido', 'Desativado']
        ).count()

        # 2. Contar clientes ativos
        clientes_ativos = Cliente.objects.filter(
            imobiliaria=tenant, 
            ativo=True
        ).count()

        # 3. Contar contratos ativos
        contratos_ativos = Contrato.objects.filter(
            imobiliaria=tenant,
            status_contrato='Ativo'
        ).count()
        
        # 4. Contar novos clientes nos últimos 30 dias
        trinta_dias_atras = timezone.now() - timedelta(days=30)
        novos_clientes = Cliente.objects.filter(
            imobiliaria=tenant,
            data_cadastro__gte=trinta_dias_atras
        ).count()

        # Compila os dados numa resposta JSON
        data = {
            'imoveis_ativos': imoveis_ativos,
            'clientes_ativos': clientes_ativos,
            'contratos_ativos': contratos_ativos,
            'novos_clientes_30d': novos_clientes,
        }
        
        return Response(data)
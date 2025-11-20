# C:\wamp64\www\ImobCloud\core\views.py

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions 
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
# ADICIONADO: Importação de Q para consultas complexas
from django.db.models import Sum, Q

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

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.tenant:
            imobiliaria_id = self.request.tenant.id
            queryset = User.objects.filter(perfil__imobiliaria_id=imobiliaria_id)
            
            # --- CORREÇÃO: FILTRO POR CARGO (ADAPTADO PARA BOOLEANOS) ---
            cargo = self.request.query_params.get('cargo')
            if cargo:
                cargo_upper = cargo.upper()
                if cargo_upper == 'ADMIN':
                    queryset = queryset.filter(perfil__is_admin=True)
                elif cargo_upper == 'CORRETOR':
                    queryset = queryset.filter(perfil__is_corretor=True)
            
            return queryset
            
        return User.objects.none()

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return CorretorDisplaySerializer
        return CorretorRegistrationSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'list':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy', 'retrieve']:
            permission_classes = [IsAdminOrSuperUser]
        elif self.action in ['me', 'minhas_notificacoes', 'marcar_notificacoes_lidas']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(imobiliaria=self.request.tenant)

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request, *args, **kwargs):
        user = request.user
        if request.method == 'GET':
            serializer = CorretorDisplaySerializer(user)
            return Response(serializer.data)
        
        serializer = CorretorRegistrationSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            display_serializer = CorretorDisplaySerializer(user)
            return Response(display_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='minhas-notificacoes')
    def minhas_notificacoes(self, request):
        notificacoes = Notificacao.objects.filter(destinatario=request.user, lida=False)
        serializer = NotificacaoSerializer(notificacoes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='marcar-notificacoes-lidas')
    def marcar_notificacoes_lidas(self, request):
        ids_notificacoes = request.data.get('ids', [])
        if not ids_notificacoes:
            return Response({"error": "Nenhum ID de notificação fornecido."}, status=status.HTTP_400_BAD_REQUEST)

        Notificacao.objects.filter(
            destinatario=request.user, 
            id__in=ids_notificacoes
        ).update(lida=True)
        
        return Response({"success": "Notificações marcadas como lidas."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrSuperUser])
    def lista_corretores_simples(self, request):
        """
        Retorna uma lista simplificada (ID, Nome) de corretores
        para uso em dropdowns (ex: transferir oportunidade).
        """
        imobiliaria = request.tenant
        
        # --- CORREÇÃO: FILTRO USANDO Q OBJECTS PARA BOOLEANOS ---
        # Lista qualquer usuário que seja Admin OU Corretor
        corretores = User.objects.filter(
            perfil__imobiliaria=imobiliaria
        ).filter(
            Q(perfil__is_admin=True) | Q(perfil__is_corretor=True)
        ).values('id', 'first_name', 'last_name', 'email')
        
        data = [
            {
                "id": corretor['id'],
                "nome_completo": f"{corretor['first_name']} {corretor['last_name']}".strip(),
                "email": corretor['email']
            }
            for corretor in corretores
        ]
        return Response(data)


class CorretorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = CorretorDisplaySerializer
    permission_classes = [IsAdminOrSuperUser]


class DashboardStatsView(APIView):
    permission_classes = [IsCorretorOrReadOnly]

    def get(self, request, *args, **kwargs):
        imobiliaria = request.tenant
        
        total_imoveis = Imovel.objects.filter(
            imobiliaria=imobiliaria, 
            status__in=['A_VENDA', 'PARA_ALUGAR']
        ).count()
        
        total_clientes = Cliente.objects.filter(
            imobiliaria=imobiliaria,
            ativo=True
        ).count()
        
        total_contratos_ativos = Contrato.objects.filter(
            imobiliaria=imobiliaria,
            status_contrato='ATIVO' 
        ).count()
        
        hoje = timezone.now().date()
        proximos_30_dias = hoje + timedelta(days=30)
        
        a_receber_contratos = Pagamento.objects.filter(
            contrato__imobiliaria=imobiliaria,
            status='PENDENTE',
            data_vencimento__gte=hoje,
            data_vencimento__lte=proximos_30_dias
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        total_a_receber = a_receber_contratos

        stats = {
            'total_imoveis': total_imoveis,
            'total_clientes': total_clientes,
            'total_contratos_ativos': total_contratos_ativos,
            'total_a_receber_30d': total_a_receber,
        }
        
        return Response(stats)
    
class IntegracaoRedesSociaisView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ImobiliariaIntegracaoSerializer

    def get(self, request, *args, **kwargs):
        imobiliaria = request.tenant
        # --- CORREÇÃO: VERIFICAÇÃO DE PERMISSÃO ATUALIZADA ---
        if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.is_admin)):
            return Response({"error": "Acesso não autorizado."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.serializer_class(imobiliaria)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        imobiliaria = request.tenant
        # --- CORREÇÃO: VERIFICAÇÃO DE PERMISSÃO ATUALIZADA ---
        if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.is_admin)):
            return Response({"error": "Acesso não autorizado."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(imobiliaria, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Credenciais salvas com sucesso!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
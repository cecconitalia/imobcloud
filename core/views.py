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
from django.db.models import Sum

# --- NOVAS IMPORTAÇÕES PARA LOGOUT ---\
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

# Importar as permissões necessárias
from .permissions import IsAdminOrSuperUser, IsCorretorOrReadOnly


User = get_user_model()

class MyTokenObtainPairView(TokenObtainPairView):
    """
    View existente para o login.
    """
    serializer_class = MyTokenObtainPairSerializer

# --- NOVA VIEW DE LOGOUT ADICIONADA ---
class LogoutView(APIView):
    """
    View para invalidar o refresh token (fazer logout).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
# --- FIM DA VIEW DE LOGOUT ---


class CorretorRegistrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para registro e gerenciamento de Corretores (Usuários).
    """
    serializer_class = CorretorRegistrationSerializer

    def get_queryset(self):
        # Apenas Admins podem listar todos os usuários da imobiliária
        if self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo == 'ADMIN'):
            imobiliaria_id = self.request.tenant.id
            return User.objects.filter(perfil__imobiliaria_id=imobiliaria_id)
        # Usuários não-admin não podem listar ninguém por este método
        return User.objects.none()

    def get_serializer_class(self):
        # Usa um serializer diferente para 'list' e 'retrieve' para não expor dados sensíveis
        if self.action == 'list' or self.action == 'retrieve':
            return CorretorDisplaySerializer
        return CorretorRegistrationSerializer

    def get_permissions(self):
        """
        Define permissões por ação.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy', 'list', 'retrieve']:
            permission_classes = [IsAdminOrSuperUser()]
        elif self.action in ['me', 'minhas_notificacoes', 'marcar_notificacoes_lidas']:
            # Usamos instâncias aqui
            permission_classes = [IsAuthenticated()]
        else:
            # Fallback seguro
            permission_classes = [IsAuthenticated()]
            
        # CORREÇÃO (TypeError): Retorna a lista de instâncias diretamente.
        return permission_classes

    def perform_create(self, serializer):
        # Define a imobiliária automaticamente baseado no subdomínio
        serializer.save(imobiliaria=self.request.tenant)

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request, *args, **kwargs):
        """
        Permite que o usuário autenticado veja e atualize seu próprio perfil.
        """
        user = request.user
        if request.method == 'GET':
            serializer = CorretorDisplaySerializer(user)
            return Response(serializer.data)
        
        # Para PUT/PATCH (atualização)
        serializer = CorretorRegistrationSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Retornamos os dados atualizados usando o serializer de display
            display_serializer = CorretorDisplaySerializer(user)
            return Response(display_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='minhas-notificacoes')
    def minhas_notificacoes(self, request):
        """
        Retorna as notificações não lidas para o usuário logado.
        """
        notificacoes = Notificacao.objects.filter(destinatario=request.user, lida=False)
        serializer = NotificacaoSerializer(notificacoes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='marcar-notificacoes-lidas')
    def marcar_notificacoes_lidas(self, request):
        """
        Marca notificações específicas como lidas.
        """
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
        corretores = User.objects.filter(
            perfil__imobiliaria=imobiliaria,
            perfil__cargo__in=[PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR]
        ).values('id', 'first_name', 'last_name', 'email')
        
        # Formata os dados para facilitar o uso no frontend
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
    """
    ViewSet para visualização pública ou restrita de corretores (exemplo).
    """
    queryset = User.objects.all()
    serializer_class = CorretorDisplaySerializer
    permission_classes = [IsAdminOrSuperUser] # Apenas Admins podem ver


class DashboardStatsView(APIView):
    """
    View para buscar estatísticas rápidas para o Dashboard.
    """
    permission_classes = [IsCorretorOrReadOnly]

    def get(self, request, *args, **kwargs):
        imobiliaria = request.tenant
        
        # 1. Total de Imóveis (Ativos)
        total_imoveis = Imovel.objects.filter(
            imobiliaria=imobiliaria, 
            status__in=['A_VENDA', 'PARA_ALUGAR']
        ).count()
        
        # 2. Total de Clientes (Ativos)
        total_clientes = Cliente.objects.filter(
            imobiliaria=imobiliaria,
            ativo=True
        ).count()
        
        # 3. Contratos Ativos
        total_contratos_ativos = Contrato.objects.filter(
            imobiliaria=imobiliaria,
            status_contrato='ATIVO' # <- Correção anterior
        ).count()
        
        # 4. Total a Receber (Próximos 30 dias)
        hoje = timezone.now().date()
        proximos_30_dias = hoje + timedelta(days=30)
        
        # ==================================================================
        # CORREÇÃO 3 (FieldError):
        # O traceback do erro 500 informou que o campo 'valor_total' não 
        # existe no modelo Pagamento. O nome correto é 'valor'.
        # ==================================================================
        a_receber_contratos = Pagamento.objects.filter(
            contrato__imobiliaria=imobiliaria,
            status='PENDENTE',
            data_vencimento__gte=hoje,
            data_vencimento__lte=proximos_30_dias
        ).aggregate(total=Sum('valor'))['total'] or 0 # <-- CORRIGIDO DE 'valor_total'
        
        # (Aqui você pode adicionar outras fontes de 'a receber', ex: app_financeiro)
        total_a_receber = a_receber_contratos

        stats = {
            'total_imoveis': total_imoveis,
            'total_clientes': total_clientes,
            'total_contratos_ativos': total_contratos_ativos,
            'total_a_receber_30d': total_a_receber,
        }
        
        return Response(stats)
    
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
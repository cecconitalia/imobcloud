# app_financeiro/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db.models import Sum, Q, F, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Categoria, ContaBancaria, Transacao
from .serializers import CategoriaSerializer, ContaBancariaSerializer, TransacaoSerializer
from core.permissions import IsCorretorOrReadOnly
from core.models import PerfilUsuario, Imobiliaria

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Categoria.objects.all()
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil:
            return Categoria.objects.filter(imobiliaria=self.request.user.perfil.imobiliaria)
        return Categoria.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            if 'imobiliaria' in self.request.data:
                imobiliaria_id = self.request.data['imobiliaria']
                imobiliaria_obj = Imobiliaria.objects.get(pk=imobiliaria_id)
                serializer.save(imobiliaria=imobiliaria_obj)
            else:
                raise PermissionDenied("Para superusuários, a imobiliária é obrigatória.")
        else:
            if not self.request.tenant:
                raise PermissionDenied("Não foi possível associar a categoria a uma imobiliária.")
            serializer.save(imobiliaria=self.request.tenant)

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar esta categoria.")

class ContaBancariaViewSet(viewsets.ModelViewSet):
    queryset = ContaBancaria.objects.all()
    serializer_class = ContaBancariaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        
        if not self.request.user.is_superuser and hasattr(self.request.user, 'perfil') and self.request.user.perfil:
            queryset = queryset.filter(imobiliaria=self.request.user.perfil.imobiliaria)

        if status_filter == 'inativo':
            return queryset.filter(ativo=False)
        
        return queryset.filter(ativo=True)

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            if 'imobiliaria' in self.request.data:
                imobiliaria_id = self.request.data['imobiliaria']
                imobiliaria_obj = Imobiliaria.objects.get(pk=imobiliaria_id)
                serializer.save(imobiliaria=imobiliaria_obj)
            else:
                raise PermissionDenied("Para superusuários, a imobiliária é obrigatória.")
        else:
            if not self.request.tenant:
                raise PermissionDenied("Não foi possível associar a conta a uma imobiliária.")
            serializer.save(imobiliaria=self.request.tenant)

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar esta conta bancária.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.ativo = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class TransacaoViewSet(viewsets.ModelViewSet):
    queryset = Transacao.objects.all()
    serializer_class = TransacaoSerializer
    permission_classes = [permissions.IsAuthenticated, IsCorretorOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Transacao.objects.all()
        # --- ATUALIZADO: Garante que o perfil e a imobiliária existem ---
        if hasattr(self.request.user, 'perfil') and self.request.user.perfil.imobiliaria:
            base_queryset = Transacao.objects.filter(imobiliaria=self.request.user.perfil.imobiliaria)
            
            # Lógica de filtro para Contas a Pagar/Receber vs. Transações Pagas
            # (Pode ser adicionado aqui no futuro se necessário)

            return base_queryset
        return Transacao.objects.none()

    def perform_create(self, serializer):
        """
        Cria uma nova transação (ou conta a pagar/receber), garantindo que a imobiliária (tenant)
        seja associada corretamente para evitar erros 500.
        """
        imobiliaria_tenant = None
        if self.request.user.is_superuser:
            if 'imobiliaria' in serializer.validated_data:
                imobiliaria_tenant = serializer.validated_data['imobiliaria']
            else:
                # Superusuários devem especificar a imobiliária
                raise ValidationError("Para superusuários, a imobiliária é obrigatória.")
        else:
            # Para usuários normais, o tenant é obtido da requisição
            imobiliaria_tenant = getattr(self.request, 'tenant', None)
            if not imobiliaria_tenant:
                raise PermissionDenied("Não foi possível associar a transação a uma imobiliária (tenant não encontrado).")

        # --- CORREÇÃO PRINCIPAL ---
        # A lógica agora lida com os novos campos (data_vencimento, status) e associa o tenant.
        serializer.save(imobiliaria=imobiliaria_tenant)

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar esta transação.")

    # --- INÍCIO DAS NOVAS AÇÕES PARA CONTAS A PAGAR/RECEBER ---

    @action(detail=False, methods=['get'], url_path='a-pagar')
    def a_pagar(self, request):
        """ Retorna uma lista de contas a pagar (despesas com status Pendente ou Atrasado). """
        contas = self.get_queryset().filter(
            tipo='DESPESA',
            status__in=['PENDENTE', 'ATRASADO']
        ).order_by('data_vencimento')
        serializer = self.get_serializer(contas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='a-receber')
    def a_receber(self, request):
        """ Retorna uma lista de contas a receber (receitas com status Pendente ou Atrasado). """
        contas = self.get_queryset().filter(
            tipo='RECEITA',
            status__in=['PENDENTE', 'ATRASADO']
        ).order_by('data_vencimento')
        serializer = self.get_serializer(contas, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'], url_path='marcar-pago')
    def marcar_pago(self, request, pk=None):
        """ Marca uma conta como paga, definindo a data de pagamento para hoje. """
        try:
            conta = self.get_object()
            if conta.status == 'PAGO':
                return Response({'status': 'Esta conta já foi marcada como paga.'}, status=status.HTTP_400_BAD_REQUEST)
            
            conta.status = 'PAGO'
            conta.data_pagamento = timezone.now().date()
            conta.save()
            return Response({'status': 'Conta marcada como paga com sucesso!'}, status=status.HTTP_200_OK)
        except Transacao.DoesNotExist:
            return Response({'error': 'Transação não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    # --- FIM DAS NOVAS AÇÕES ---

    # Suas ações existentes 'stats' e 'dre' foram mantidas, mas atualizadas
    # para usar 'data_vencimento' em vez de 'data'.

    @action(detail=False, methods=['get'])
    def stats(self, request):
        if not hasattr(request.user, 'perfil') or not request.user.perfil:
            return Response({"error": "Usuário sem perfil associado."}, status=status.HTTP_400_BAD_REQUEST)
        
        hoje = timezone.now().date()
        inicio_do_mes = hoje.replace(day=1)

        # ATUALIZADO: Filtra por 'data_vencimento' e status 'PAGO' para estatísticas
        transacoes_mes = self.get_queryset().filter(
            status='PAGO',
            data_pagamento__gte=inicio_do_mes,
            data_pagamento__lte=hoje
        )

        total_receitas = transacoes_mes.filter(tipo='RECEITA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
        total_despesas = transacoes_mes.filter(tipo='DESPESA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
        saldo_mes = total_receitas - total_despesas

        return Response({
            "receitas_mes": total_receitas,
            "despesas_mes": total_despesas,
            "saldo_mes": saldo_mes
        })
    
    @action(detail=False, methods=['get'])
    def dre(self, request):
        if not hasattr(request.user, 'perfil') or not request.user.perfil:
            return Response({"error": "Usuário sem perfil associado."}, status=status.HTTP_400_BAD_REQUEST)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # ATUALIZADO: Filtra por 'data_pagamento' e status 'PAGO' para o DRE
        transacoes = self.get_queryset().filter(status='PAGO')
        if start_date:
            transacoes = transacoes.filter(data_pagamento__gte=start_date)
        if end_date:
            transacoes = transacoes.filter(data_pagamento__lte=end_date)
            
        receitas_brutas = transacoes.filter(tipo='RECEITA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
        despesas_operacionais = transacoes.filter(tipo='DESPESA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']

        # A lógica do seu DRE foi mantida
        dre_data = {
            "receita_bruta_servicos": {"titulo": "Receita Bruta", "valor": receitas_brutas, "subcategorias": []},
            "deducoes_receita": {"titulo": "Deduções da Receita Bruta", "valor": 0, "subcategorias": []},
            "custo_servicos": {"titulo": "Custo dos Serviços Prestados", "valor": 0, "subcategorias": []},
            "lucro_bruto": {"titulo": "Lucro Bruto", "valor": receitas_brutas},
            "despesas_operacionais": {"titulo": "Despesas Operacionais", "valor": despesas_operacionais, "subcategorias": []},
            "lucro_liquido_antes_impostos": {"titulo": "Lucro Líquido Antes dos Impostos", "valor": receitas_brutas - despesas_operacionais},
        }

        for categoria in Categoria.objects.filter(imobiliaria=request.user.perfil.imobiliaria, pai__isnull=True):
            subcategorias_data = []
            for subcategoria in categoria.subcategorias.all():
                subtotal = transacoes.filter(categoria=subcategoria).aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
                subcategorias_data.append({"titulo": subcategoria.nome, "valor": subtotal})
            
            total_categoria = transacoes.filter(categoria=categoria).aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
            
            if categoria.tipo == 'RECEITA':
                dre_data["receita_bruta_servicos"]["subcategorias"].append({"titulo": categoria.nome, "valor": total_categoria, "subcategorias": subcategorias_data})
            elif categoria.tipo == 'DESPESA':
                dre_data["despesas_operacionais"]["subcategorias"].append({"titulo": categoria.nome, "valor": total_categoria, "subcategorias": subcategorias_data})

        return Response(dre_data)
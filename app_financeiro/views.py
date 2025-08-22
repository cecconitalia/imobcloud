# app_financeiro/views.py

from rest_framework import viewsets, permissions, status, filters # <<< IMPORTAR FILTERS
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db.models import Sum, Q, F, DecimalField, Count
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Categoria, ContaBancaria, Transacao, FormaPagamento
from .serializers import CategoriaSerializer, ContaBancariaSerializer, TransacaoSerializer, FormaPagamentoSerializer
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
            return Categoria.objects.filter(Q(imobiliaria=self.request.user.perfil.imobiliaria) | Q(imobiliaria__isnull=True))
        return Categoria.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            imobiliaria_id = self.request.data.get('imobiliaria')
            imobiliaria_obj = None
            if imobiliaria_id:
                imobiliaria_obj = Imobiliaria.objects.get(pk=imobiliaria_id)
            serializer.save(imobiliaria=imobiliaria_obj)
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
        if self.request.user.is_superuser:
            return ContaBancaria.objects.all()
        
        queryset = ContaBancaria.objects.filter(imobiliaria=self.request.user.perfil.imobiliaria)
        
        if self.action == 'list':
            status_filter = self.request.query_params.get('status')
            if status_filter == 'inativo':
                return queryset.filter(ativo=False)
            
            return queryset.filter(ativo=True)
            
        return queryset

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

class FormaPagamentoViewSet(viewsets.ModelViewSet):
    queryset = FormaPagamento.objects.all()
    serializer_class = FormaPagamentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return FormaPagamento.objects.all()
        return FormaPagamento.objects.filter(imobiliaria=self.request.tenant, ativo=True)

    def perform_create(self, serializer):
        if not self.request.tenant:
            raise PermissionDenied("Forma de pagamento não pode ser associada a uma imobiliária.")
        serializer.save(imobiliaria=self.request.tenant)
        
class TransacaoViewSet(viewsets.ModelViewSet):
    queryset = Transacao.objects.all()
    serializer_class = TransacaoSerializer
    permission_classes = [permissions.IsAuthenticated, IsCorretorOrReadOnly]
    # ==========================================================================================
    # <<< HABILITANDO O BACKEND DE BUSCA >>>
    filter_backends = [filters.SearchFilter]
    search_fields = ['descricao', 'contrato__inquilino__nome_completo', 'contrato__id']
    # ==========================================================================================


    def get_queryset(self):
        if self.request.user.is_superuser:
            base_queryset = Transacao.objects.all()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.imobiliaria:
            base_queryset = Transacao.objects.filter(imobiliaria=self.request.user.perfil.imobiliaria)
        else:
            return Transacao.objects.none()

        params = self.request.query_params

        categoria_id = params.get('categoria')
        if categoria_id:
            base_queryset = base_queryset.filter(categoria_id=categoria_id)

        start_date = params.get('start_date')
        end_date = params.get('end_date')
        if start_date:
            base_queryset = base_queryset.filter(data_vencimento__gte=start_date)
        if end_date:
            base_queryset = base_queryset.filter(data_vencimento__lte=end_date)
        
        ordering = params.get('ordering')
        if ordering in ['valor', '-valor', 'data_vencimento', '-data_vencimento']:
            base_queryset = base_queryset.order_by(ordering)
        
        return base_queryset.select_related('categoria', 'contrato__inquilino', 'imovel')


    def perform_create(self, serializer):
        imobiliaria_tenant = None
        if self.request.user.is_superuser:
            if 'imobiliaria' in serializer.validated_data:
                imobiliaria_tenant = serializer.validated_data['imobiliaria']
            else:
                raise ValidationError("Para superusuários, a imobiliária é obrigatória.")
        else:
            imobiliaria_tenant = getattr(self.request, 'tenant', None)
            if not imobiliaria_tenant:
                raise PermissionDenied("Não foi possível associar a transação a uma imobiliária (tenant não encontrado).")
        serializer.save(imobiliaria=imobiliaria_tenant)

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar esta transação.")
            
    def list(self, request, *args, **kwargs):
        # Sobrescreve o método `list` para aplicar a busca antes da filtragem de `a_pagar`/`a_receber`
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='a-pagar')
    def a_pagar(self, request):
        queryset = self.filter_queryset(self.get_queryset()) # Aplica a busca (search)
        contas = queryset.filter(
            tipo='DESPESA',
            status__in=['PENDENTE', 'ATRASADO']
        )
        serializer = self.get_serializer(contas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='a-receber')
    def a_receber(self, request):
        queryset = self.filter_queryset(self.get_queryset()) # Aplica a busca (search)
        contas = queryset.filter(
            tipo='RECEITA',
            status__in=['PENDENTE', 'ATRASADO']
        )
        serializer = self.get_serializer(contas, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'], url_path='marcar-pago')
    def marcar_pago(self, request, pk=None):
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

    @action(detail=False, methods=['get'])
    def stats(self, request):
        if not hasattr(request.user, 'perfil') or not request.user.perfil:
            return Response({"error": "Usuário sem perfil associado."}, status=status.HTTP_400_BAD_REQUEST)
        
        hoje = timezone.now().date()
        inicio_do_mes = hoje.replace(day=1)

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
    
    @action(detail=False, methods=['get'], url_path='contas-pendentes-stats')
    def contas_pendentes_stats(self, request):
        queryset = self.get_queryset().filter(status__in=['PENDENTE', 'ATRASADO'])
        hoje = timezone.now().date()

        total_a_receber = queryset.filter(tipo='RECEITA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
        total_a_pagar = queryset.filter(tipo='DESPESA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
        
        contas_vencidas = queryset.filter(data_vencimento__lt=hoje)
        total_vencido = contas_vencidas.aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
        quantidade_vencidas = contas_vencidas.count()

        return Response({
            "total_a_receber": total_a_receber,
            "total_a_pagar": total_a_pagar,
            "total_vencido": total_vencido,
            "quantidade_vencidas": quantidade_vencidas
        })
    
    @action(detail=False, methods=['get'])
    def dre(self, request):
        if not hasattr(request.user, 'perfil') or not request.user.perfil:
            return Response({"error": "Usuário sem perfil associado."}, status=status.HTTP_400_BAD_REQUEST)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        transacoes = self.get_queryset().filter(status='PAGO')
        if start_date:
            transacoes = transacoes.filter(data_pagamento__gte=start_date)
        if end_date:
            transacoes = transacoes.filter(data_pagamento__lte=end_date)
            
        receitas_brutas = transacoes.filter(tipo='RECEITA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']
        despesas_operacionais = transacoes.filter(tipo='DESPESA').aggregate(total=Coalesce(Sum('valor'), 0, output_field=DecimalField()))['total']

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
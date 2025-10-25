# C:\wamp64\www\ImobCloud\app_financeiro\views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from .models import Categoria, Conta, Transacao, FormaPagamento
from .serializers import (
    CategoriaSerializer, 
    ContaSerializer,
    TransacaoSerializer, 
    FormaPagamentoSerializer,
    TransacaoListSerializer
)
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.views import APIView

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Categoria.objects.filter(imobiliaria=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(imobiliaria=self.request.tenant)

class ContaViewSet(viewsets.ModelViewSet):
    queryset = Conta.objects.all()
    serializer_class = ContaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conta.objects.filter(imobiliaria=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(imobiliaria=self.request.tenant)

class FormaPagamentoViewSet(viewsets.ModelViewSet):
    queryset = FormaPagamento.objects.all()
    serializer_class = FormaPagamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FormaPagamento.objects.filter(imobiliaria=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(imobiliaria=self.request.tenant)

class TransacaoViewSet(viewsets.ModelViewSet):
    queryset = Transacao.objects.all()
    serializer_class = TransacaoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transacao.objects.filter(imobiliaria=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(imobiliaria=self.request.tenant)
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = TransacaoListSerializer(queryset, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        today = timezone.now().date()
        a_receber_pendente = queryset.filter(tipo='RECEITA', status__in=['PENDENTE', 'ATRASADO']).aggregate(total=Sum('valor'))['total'] or 0
        a_receber_pago_mes = queryset.filter(tipo='RECEITA', status='PAGO', data_transacao__month=today.month, data_transacao__year=today.year).aggregate(total=Sum('valor'))['total'] or 0
        a_pagar_pendente = queryset.filter(tipo='DESPESA', status__in=['PENDENTE', 'ATRASADO']).aggregate(total=Sum('valor'))['total'] or 0
        a_pagar_pago_mes = queryset.filter(tipo='DESPESA', status='PAGO', data_transacao__month=today.month, data_transacao__year=today.year).aggregate(total=Sum('valor'))['total'] or 0
        stats_data = {
            'a_receber': {'pendente': a_receber_pendente, 'pago_mes_atual': a_receber_pago_mes},
            'a_pagar': {'pendente': a_pagar_pendente, 'pago_mes_atual': a_pagar_pago_mes},
            'saldo_previsto': a_receber_pendente - a_pagar_pendente
        }
        return Response(stats_data)

    # ADICIONADO: Endpoint para listar apenas contas a receber
    @action(detail=False, methods=['get'], url_path='a-receber')
    def a_receber(self, request):
        queryset = self.get_queryset().filter(tipo='RECEITA').order_by('data_vencimento')
        serializer = TransacaoListSerializer(queryset, many=True)
        return Response(serializer.data)

    # ADICIONADO: Endpoint para listar apenas contas a pagar
    @action(detail=False, methods=['get'], url_path='a-pagar')
    def a_pagar(self, request):
        queryset = self.get_queryset().filter(tipo='DESPESA').order_by('data_vencimento')
        serializer = TransacaoListSerializer(queryset, many=True)
        return Response(serializer.data)

    # ADICIONADO: Endpoint para estatísticas de contas pendentes
    @action(detail=False, methods=['get'], url_path='contas-pendentes-stats')
    def contas_pendentes_stats(self, request):
        queryset = self.get_queryset()
        total_a_receber = queryset.filter(tipo='RECEITA', status__in=['PENDENTE', 'ATRASADO']).aggregate(total=Sum('valor'))['total'] or 0
        total_a_pagar = queryset.filter(tipo='DESPESA', status__in=['PENDENTE', 'ATRASADO']).aggregate(total=Sum('valor'))['total'] or 0
        return Response({
            'total_a_receber': total_a_receber,
            'total_a_pagar': total_a_pagar
        })


class DREViewAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        if not start_date_str or not end_date_str:
            return Response({"error": "As datas de início e fim são obrigatórias."}, status=status.HTTP_400_BAD_REQUEST)
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
        if not start_date or not end_date:
            return Response({"error": "Formato de data inválido. Use AAAA-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        queryset = Transacao.objects.filter(imobiliaria=request.tenant, data_transacao__range=[start_date, end_date], status='PAGO')
        receitas = queryset.filter(tipo='RECEITA').values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')
        despesas = queryset.filter(tipo='DESPESA').values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')
        total_receitas = sum(item['total'] for item in receitas if item['total'])
        total_despesas = sum(item['total'] for item in despesas if item['total'])
        lucro_liquido = total_receitas - total_despesas
        return Response({
            'receitas_por_categoria': list(receitas),
            'despesas_por_categoria': list(despesas),
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'lucro_liquido': lucro_liquido,
        })
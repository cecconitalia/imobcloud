# C:\wamp64\www\ImobCloud\app_financeiro\views.py

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
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
from django.db.models import Sum, Q, Case, When, DecimalField
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from decimal import Decimal 
from datetime import timedelta, date 

from app_clientes.models import Cliente

try:
    from ImobCloud.utils.formatacao_util import apenas_numeros
except ImportError:
    def apenas_numeros(text):
        if text is None: return ''
        return ''.join(filter(str.isdigit, str(text)))

# --- Paginação Padrão ---
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

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
    serializer_class = TransacaoListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'retrieve']:
            return TransacaoSerializer
        return TransacaoListSerializer

    def get_queryset(self):
        # 1. Filtro Base
        queryset = Transacao.objects.filter(imobiliaria=self.request.tenant)

        # 2. Captura os parâmetros
        params = self.request.query_params
        
        # Filtros
        tipo = params.get('tipo')
        if tipo: queryset = queryset.filter(tipo=tipo)

        status_filter = params.get('status')
        if status_filter: queryset = queryset.filter(status=status_filter)

        categoria = params.get('categoria')
        if categoria: queryset = queryset.filter(categoria_id=categoria)

        conta = params.get('conta')
        if conta: queryset = queryset.filter(conta_id=conta)

        # Filtro de Data
        data_inicio = params.get('data_vencimento__gte') or params.get('data_inicio')
        data_fim = params.get('data_vencimento__lte') or params.get('data_fim')
        
        if data_inicio:
            dt_ini = parse_date(data_inicio)
            if dt_ini: queryset = queryset.filter(data_vencimento__gte=dt_ini)
            
        if data_fim:
            dt_fim = parse_date(data_fim)
            if dt_fim: queryset = queryset.filter(data_vencimento__lte=dt_fim)

        # Filtro de Busca
        search = params.get('search')
        cliente_id = params.get('cliente_id')

        if cliente_id:
            queryset = queryset.filter(
                Q(cliente_id=cliente_id) | 
                Q(contrato__inquilino_id=cliente_id) | 
                Q(contrato__proprietario_id=cliente_id)
            )
        
        if search:
            doc_limpo = apenas_numeros(search)
            if len(doc_limpo) >= 11:
                clientes_ids = Cliente.objects.filter(
                    documento=doc_limpo, 
                    imobiliaria=self.request.tenant
                ).values_list('id', flat=True)
                
                queryset = queryset.filter(
                    Q(cliente_id__in=clientes_ids) | 
                    Q(contrato__inquilino_id__in=clientes_ids) | 
                    Q(contrato__proprietario_id__in=clientes_ids)
                )
            else:
                queryset = queryset.filter(
                    Q(descricao__icontains=search) |
                    Q(observacoes__icontains=search) |
                    Q(cliente__nome__icontains=search) |
                    Q(cliente__razao_social__icontains=search)
                )

        return queryset.order_by('-data_vencimento', '-id')

    def perform_create(self, serializer):
        serializer.save(imobiliaria=self.request.tenant)
        
    def perform_update(self, serializer):
        instance = serializer.instance
        status_anterior = instance.status
        novo_status = serializer.validated_data.get('status')
        data_pagamento_receita = serializer.validated_data.get('data_pagamento')
        
        serializer.save(imobiliaria=self.request.tenant)
        
        is_aluguel_pago_agora = (
            instance.tipo == 'RECEITA' and 
            instance.contrato and 
            instance.contrato.tipo_contrato == 'ALUGUEL' and 
            novo_status == 'PAGO' and 
            status_anterior != 'PAGO'
        )

        if is_aluguel_pago_agora:
            self._criar_transacao_repasse(instance, data_pagamento_receita)

    def _criar_transacao_repasse(self, transacao_receita: Transacao, data_pagamento_receita):
        if Transacao.objects.filter(transacao_origem=transacao_receita).exists():
            return
        contrato = transacao_receita.contrato
        if not contrato.imovel or not contrato.proprietario:
            return
        
        try:
            taxa = contrato.taxa_administracao_percentual
            comissao = transacao_receita.valor * (taxa / Decimal(100))
            repasse = transacao_receita.valor - comissao
        except Exception:
            return
        
        try:
            categoria_repasse, _ = Categoria.objects.get_or_create(
                imobiliaria=transacao_receita.imobiliaria,
                nome='Repasse de Aluguel',
                tipo='DESPESA'
            )
        except Exception:
            return
            
        if data_pagamento_receita and isinstance(data_pagamento_receita, date):
            data_base = data_pagamento_receita
        else:
            data_base = timezone.now().date()

        data_venc = data_base + timedelta(days=5)
        logradouro = getattr(transacao_receita.imovel, 'logradouro', 'Imóvel')
        ref = transacao_receita.data_vencimento.strftime('%m/%Y')

        Transacao.objects.create(
            imobiliaria=transacao_receita.imobiliaria,
            descricao=f"Repasse Aluguel: {logradouro} (Ref: {ref})",
            valor=repasse,
            tipo='DESPESA',
            status='PENDENTE',
            data_transacao=data_base, 
            data_vencimento=data_venc,
            categoria=categoria_repasse,
            cliente=contrato.proprietario,
            imovel=transacao_receita.imovel,
            contrato=contrato,
            transacao_origem=transacao_receita,
            observacoes=f"Repasse automático. Comissão {taxa}% retida."
        )

    # --- ENDPOINT ATUALIZADO: Totais Filtrados + Nome da Imobiliária ---
    @action(detail=False, methods=['get'], url_path='resumo-filtros')
    def resumo_filtros(self, request):
        """
        Retorna o somatório e o nome da imobiliária atual.
        """
        queryset = self.get_queryset()
        
        aggregates = queryset.aggregate(
            total_receitas=Sum(Case(When(tipo='RECEITA', then='valor'), default=0, output_field=DecimalField())),
            total_despesas=Sum(Case(When(tipo='DESPESA', then='valor'), default=0, output_field=DecimalField()))
        )
        
        receitas = aggregates['total_receitas'] or 0
        despesas = aggregates['total_despesas'] or 0
        
        # Pega o nome da imobiliária do tenant atual
        nome_imobiliaria = getattr(request.tenant, 'nome', 'Imobiliária')
        
        return Response({
            'receitas': receitas,
            'despesas': despesas,
            'saldo': receitas - despesas,
            'nome_imobiliaria': nome_imobiliaria  # <--- CAMPO NOVO
        })

    @action(detail=False, methods=['get'], url_path='a-receber')
    def a_receber(self, request):
        queryset = self.get_queryset().filter(tipo='RECEITA')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='a-pagar')
    def a_pagar(self, request):
        queryset = self.get_queryset().filter(tipo='DESPESA')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset() 
        today = timezone.now().date()
        
        aggregates = queryset.aggregate(
            a_receber_pendente=Sum(Case(When(tipo='RECEITA', status__in=['PENDENTE', 'ATRASADO'], then='valor'), default=0, output_field=DecimalField())),
            a_receber_pago_mes=Sum(Case(When(tipo='RECEITA', status='PAGO', data_pagamento__month=today.month, data_pagamento__year=today.year, then='valor'), default=0, output_field=DecimalField())),
            a_pagar_pendente=Sum(Case(When(tipo='DESPESA', status__in=['PENDENTE', 'ATRASADO'], then='valor'), default=0, output_field=DecimalField())),
            a_pagar_pago_mes=Sum(Case(When(tipo='DESPESA', status='PAGO', data_pagamento__month=today.month, data_pagamento__year=today.year, then='valor'), default=0, output_field=DecimalField()))
        )

        return Response({
            'a_receber': {
                'pendente': aggregates['a_receber_pendente'] or 0,
                'pago_mes_atual': aggregates['a_receber_pago_mes'] or 0
            },
            'a_pagar': {
                'pendente': aggregates['a_pagar_pendente'] or 0,
                'pago_mes_atual': aggregates['a_pagar_pago_mes'] or 0
            },
            'saldo_previsto': (aggregates['a_receber_pendente'] or 0) - (aggregates['a_pagar_pendente'] or 0)
        })

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
            return Response({"error": "Datas obrigatórias."}, status=status.HTTP_400_BAD_REQUEST)
        
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
        
        if not start_date or not end_date:
            return Response({"error": "Data inválida."}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Transacao.objects.filter(
            imobiliaria=request.tenant, 
            data_pagamento__range=[start_date, end_date], 
            status='PAGO'
        )
        
        receitas = queryset.filter(tipo='RECEITA').values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')
        despesas = queryset.filter(tipo='DESPESA').values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')
        
        total_receitas = sum(item['total'] for item in receitas if item['total'])
        total_despesas = sum(item['total'] for item in despesas if item['total'])
        
        return Response({
            'receitas_por_categoria': list(receitas),
            'despesas_por_categoria': list(despesas),
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'lucro_liquido': total_receitas - total_despesas,
        })
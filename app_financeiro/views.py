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
from django.db.models import Sum, Q, Case, When, DecimalField, F
from django.db.models.functions import TruncMonth, TruncDay, Coalesce
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from decimal import Decimal 
from datetime import timedelta, date, datetime
import math
import logging

from app_clientes.models import Cliente
from core.models import Imobiliaria

logger = logging.getLogger(__name__)

try:
    from ImobCloud.utils.formatacao_util import apenas_numeros
except ImportError:
    def apenas_numeros(text):
        if text is None: return ''
        return ''.join(filter(str.isdigit, str(text)))

def safe_float_conversion(value):
    """Converte valores Decimal ou None para float de forma segura para JSON."""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
             return Categoria.objects.filter(imobiliaria=tenant)
        return Categoria.objects.none()

    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            serializer.save(imobiliaria=tenant)

class ContaViewSet(viewsets.ModelViewSet):
    queryset = Conta.objects.all()
    serializer_class = ContaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
             return Conta.objects.filter(imobiliaria=tenant)
        return Conta.objects.none()

    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            serializer.save(imobiliaria=tenant)

class FormaPagamentoViewSet(viewsets.ModelViewSet):
    queryset = FormaPagamento.objects.all()
    serializer_class = FormaPagamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
             return FormaPagamento.objects.filter(imobiliaria=tenant)
        return FormaPagamento.objects.none()

    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None)
        if tenant:
            serializer.save(imobiliaria=tenant)

# --- VIEW DEDICADA PARA O DASHBOARD (CORREÇÃO DE 500) ---
class FinanceiroStatsView(APIView):
    """
    View para retornar KPIs financeiros básicos.
    Retorna JSON com floats seguros.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            tenant = getattr(request, 'tenant', None) or getattr(user, 'imobiliaria', None)

            if not tenant:
                # Se não tem tenant, retorna zerado para evitar erro
                return Response({
                    "receita_mes": 0.0,
                    "previsto_entrada": 0.0,
                    "previsto_saida": 0.0
                })

            qs = Transacao.objects.filter(imobiliaria=tenant)
            
            hoje = timezone.now().date()
            inicio_mes = hoje.replace(day=1)
            # Lógica segura para fim do mês
            proximo_mes = (inicio_mes + timedelta(days=32)).replace(day=1)
            fim_mes = proximo_mes - timedelta(days=1)

            # 1. Receita Realizada (PAGO)
            # Importante: verifica se data_pagamento não é nula
            receita_mes_dec = qs.filter(
                tipo='RECEITA',
                status='PAGO',
                data_pagamento__range=[inicio_mes, fim_mes]
            ).aggregate(total=Sum('valor'))['total'] or Decimal(0)

            # 2. Previsão Entrada (PAGO + PENDENTE por Vencimento)
            previsto_entrada_dec = qs.filter(
                tipo='RECEITA',
                data_vencimento__range=[inicio_mes, fim_mes]
            ).aggregate(total=Sum('valor'))['total'] or Decimal(0)

            # 3. Previsão Saída (PAGO + PENDENTE por Vencimento)
            previsto_saida_dec = qs.filter(
                tipo='DESPESA',
                data_vencimento__range=[inicio_mes, fim_mes]
            ).aggregate(total=Sum('valor'))['total'] or Decimal(0)

            return Response({
                "receita_mes": safe_float_conversion(receita_mes_dec),
                "previsto_entrada": safe_float_conversion(previsto_entrada_dec),
                "previsto_saida": safe_float_conversion(previsto_saida_dec)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Log do erro para debug no console do servidor
            import traceback
            traceback.print_exc()
            logger.error(f"Erro em FinanceiroStatsView: {e}")
            # Retorna o erro detalhado no JSON (apenas para dev/debug)
            return Response(
                {"error": "Erro interno ao calcular finanças", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransacaoViewSet(viewsets.ModelViewSet):
    queryset = Transacao.objects.all()
    serializer_class = TransacaoListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'retrieve']:
            return TransacaoSerializer
        return TransacaoListSerializer

    def _get_tenant(self):
        tenant = getattr(self.request, 'tenant', None)
        if not tenant and hasattr(self.request.user, 'imobiliaria'):
            tenant = self.request.user.imobiliaria
        # Fallbacks removidos para evitar vazamento de dados entre tenants
        return tenant

    def get_queryset(self):
        tenant = self._get_tenant()
        if not tenant:
            return Transacao.objects.none()

        queryset = Transacao.objects.filter(imobiliaria=tenant)
        params = self.request.query_params
        
        tipo = params.get('tipo')
        if tipo: queryset = queryset.filter(tipo=tipo)

        status_filter = params.get('status')
        if status_filter: queryset = queryset.filter(status=status_filter)

        categoria = params.get('categoria')
        if categoria: queryset = queryset.filter(categoria_id=categoria)

        conta = params.get('conta')
        if conta: queryset = queryset.filter(conta_id=conta)

        imovel = params.get('imovel')
        if imovel: queryset = queryset.filter(imovel_id=imovel)

        # Filtros de data
        data_inicio = params.get('data_vencimento__gte') or params.get('data_inicio')
        data_fim = params.get('data_vencimento__lte') or params.get('data_fim')
        
        if data_inicio:
            dt_ini = parse_date(data_inicio)
            if dt_ini: queryset = queryset.filter(data_vencimento__gte=dt_ini)
            
        if data_fim:
            dt_fim = parse_date(data_fim)
            if dt_fim: queryset = queryset.filter(data_vencimento__lte=dt_fim)

        # Filtro de Cliente
        cliente_id = params.get('cliente_id')
        if cliente_id:
            queryset = queryset.filter(
                Q(cliente_id=cliente_id) | 
                Q(contrato__inquilino_id=cliente_id) | 
                Q(contrato__proprietario_id=cliente_id)
            )
        
        # Busca Textual
        search = params.get('search')
        if search:
            doc_limpo = apenas_numeros(search)
            if len(doc_limpo) >= 11:
                clientes_ids = Cliente.objects.filter(
                    documento=doc_limpo, 
                    imobiliaria=tenant
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
                    Q(cliente__razao_social__icontains=search) |
                    Q(imovel__titulo_anuncio__icontains=search) |
                    Q(imovel__logradouro__icontains=search) |
                    Q(imovel__codigo_referencia__icontains=search)
                )

        ordenacao = params.get('ordenacao')
        if ordenacao:
            queryset = queryset.order_by(ordenacao)
        else:
            # Padrão alterado para crescente (data_vencimento)
            queryset = queryset.order_by('data_vencimento', 'id')

        return queryset

    def perform_create(self, serializer):
        tenant = self._get_tenant()
        if not tenant:
            raise Exception("Imobiliária não identificada para criar transação.")
        serializer.save(imobiliaria=tenant)
        
    def perform_update(self, serializer):
        tenant = self._get_tenant()
        if not tenant:
            raise Exception("Imobiliária não identificada para atualizar transação.")

        instance = serializer.instance
        status_anterior = instance.status
        novo_status = serializer.validated_data.get('status')
        data_pagamento_receita = serializer.validated_data.get('data_pagamento')
        
        serializer.save(imobiliaria=tenant)
        
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

    # --- ACTIONS PARA CORRIGIR ERRO 404 (Mantidas para compatibilidade) ---
    @action(detail=False, methods=['get'], url_path='a-receber')
    def a_receber(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(tipo='RECEITA')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='a-pagar')
    def a_pagar(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(tipo='DESPESA')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # Action legada stats (dentro de transacoes)
    @action(detail=False, methods=['get'])
    def stats(self, request):
        # Redireciona logicamente para a view dedicada se chamado via ViewSet
        view = FinanceiroStatsView()
        # Injeta request
        view.request = request
        view.format_kwarg = None
        return view.get(request)

    @action(detail=False, methods=['get'], url_path='dashboard-general-stats')
    def dashboard_general_stats(self, request):
        try:
            tenant = self._get_tenant()
            if not tenant:
                return Response({})

            # 1. Ranking de Imóveis
            ranking_imoveis = Transacao.objects.filter(
                imobiliaria=tenant, tipo='DESPESA', imovel__isnull=False
            ).values('imovel__titulo_anuncio', 'imovel__logradouro').annotate(
                total=Sum('valor')
            ).order_by('-total')[:5]

            ranking_data = []
            for item in ranking_imoveis:
                nome = item['imovel__titulo_anuncio'] or item['imovel__logradouro'] or 'Sem Nome'
                ranking_data.append({
                    'label': nome,
                    'value': safe_float_conversion(item['total'])
                })

            # 2. Despesas por Categoria
            categorias = Transacao.objects.filter(
                imobiliaria=tenant, tipo='DESPESA'
            ).values('categoria__nome').annotate(
                total=Sum('valor')
            ).order_by('-total')[:5]

            categorias_data = [{
                'label': item['categoria__nome'], 
                'value': safe_float_conversion(item['total'])
            } for item in categorias]

            # 3. Evolução Financeira (Mensal)
            seis_meses_atras = timezone.now().date().replace(day=1) - timedelta(days=180)
            evolucao = Transacao.objects.filter(
                imobiliaria=tenant,
                data_pagamento__gte=seis_meses_atras,
                status='PAGO'
            ).annotate(
                mes=TruncMonth('data_pagamento')
            ).values('mes').annotate(
                receitas=Sum(Case(When(tipo='RECEITA', then='valor'), default=0, output_field=DecimalField(max_digits=19, decimal_places=2))),
                despesas=Sum(Case(When(tipo='DESPESA', then='valor'), default=0, output_field=DecimalField(max_digits=19, decimal_places=2)))
            ).order_by('mes')

            evolucao_data = []
            for item in evolucao:
                if item['mes']:
                    evolucao_data.append({
                        'mes': item['mes'].strftime('%b/%Y'),
                        'receitas': safe_float_conversion(item['receitas']),
                        'despesas': safe_float_conversion(item['despesas'])
                    })

            # 4. Balanço Diário (Blindado)
            hoje = timezone.now().date()
            inicio_mes = hoje.replace(day=1)
            proximo_mes = (inicio_mes + timedelta(days=32)).replace(day=1)
            fim_mes = proximo_mes - timedelta(days=1)

            diario_qs = Transacao.objects.filter(
                imobiliaria=tenant,
                data_pagamento__range=[inicio_mes, fim_mes],
                status='PAGO'
            ).annotate(
                dia=TruncDay('data_pagamento')
            ).values('dia').annotate(
                receitas=Sum(Case(When(tipo='RECEITA', then='valor'), default=0, output_field=DecimalField(max_digits=19, decimal_places=2))),
                despesas=Sum(Case(When(tipo='DESPESA', then='valor'), default=0, output_field=DecimalField(max_digits=19, decimal_places=2)))
            ).order_by('dia')

            dados_existentes = {}
            for item in diario_qs:
                if item['dia']:
                    chave = item['dia'].strftime('%Y-%m-%d') if hasattr(item['dia'], 'strftime') else str(item['dia'])[:10]
                    dados_existentes[chave] = item

            balanco_diario_data = []
            data_atual = inicio_mes

            while data_atual <= fim_mes:
                chave_atual = data_atual.strftime('%Y-%m-%d')
                dados = dados_existentes.get(chave_atual)
                
                receita_val = safe_float_conversion(dados['receitas']) if dados else 0.0
                despesa_val = safe_float_conversion(dados['despesas']) if dados else 0.0

                balanco_diario_data.append({
                    'dia': data_atual.strftime('%d/%m'),
                    'receitas': receita_val,
                    'despesas': despesa_val
                })
                
                data_atual += timedelta(days=1)

            return Response({
                'ranking_imoveis': ranking_data,
                'despesas_categoria': categorias_data,
                'evolucao_financeira': evolucao_data,
                'balanco_diario': balanco_diario_data
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)

class DREViewAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            tenant = getattr(request, 'tenant', None)
            if not tenant and hasattr(request.user, 'imobiliaria'):
                tenant = request.user.imobiliaria
            
            if not tenant:
                 return Response({"error": "Imobiliária não encontrada."}, status=status.HTTP_400_BAD_REQUEST)

            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            if not start_date_str or not end_date_str:
                return Response({"error": "Datas obrigatórias."}, status=status.HTTP_400_BAD_REQUEST)
            
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            
            if not start_date or not end_date:
                return Response({"error": "Data inválida."}, status=status.HTTP_400_BAD_REQUEST)
            
            queryset = Transacao.objects.filter(
                imobiliaria=tenant, 
                data_pagamento__range=[start_date, end_date], 
                status='PAGO'
            )
            
            receitas = queryset.filter(tipo='RECEITA').values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')
            despesas = queryset.filter(tipo='DESPESA').values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')
            
            total_receitas = sum(item['total'] for item in receitas if item['total'])
            total_despesas = sum(item['total'] for item in despesas if item['total'])
            
            def convert_list(data_list):
                return [{
                    'categoria__nome': item['categoria__nome'], 
                    'total': safe_float_conversion(item['total'])
                } for item in data_list]

            return Response({
                'receitas_por_categoria': convert_list(receitas),
                'despesas_por_categoria': convert_list(despesas),
                'total_receitas': safe_float_conversion(total_receitas),
                'total_despesas': safe_float_conversion(total_despesas),
                'lucro_liquido': safe_float_conversion(total_receitas - total_despesas),
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)
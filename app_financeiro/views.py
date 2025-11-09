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
from django.db.models import Sum, Q, Case, When, DecimalField
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from decimal import Decimal 
from datetime import timedelta, date 

# Importa a Model Cliente para buscar por nome/documento
from app_clientes.models import Cliente
# Importa a função de limpeza de números (assumindo que existe)
try:
    from ImobCloud.utils.formatacao_util import apenas_numeros
except ImportError:
    # Fallback se a função não for encontrada no caminho esperado
    def apenas_numeros(text):
        if text is None: return ''
        return ''.join(filter(str.isdigit, str(text)))


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
        
    def perform_update(self, serializer):
        instance = serializer.instance
        
        status_anterior = instance.status
        novo_status = serializer.validated_data.get('status')
        data_pagamento_receita = serializer.validated_data.get('data_pagamento')
        
        # Salva a transação
        serializer.save(imobiliaria=self.request.tenant)
        
        # Lógica de repasse automático (Gatilho)
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
        """
        Cria a transação de DESPESA para o proprietário com o valor do repasse.
        A categoria é criada automaticamente (self-healing) se não existir para o tenant.
        """
        # 1. Verifica se o repasse já existe (evita duplicação)
        if Transacao.objects.filter(transacao_origem=transacao_receita).exists():
            return
            
        contrato = transacao_receita.contrato
        
        # 2. VALIDAÇÃO DE PRÉ-REQUISITOS CRÍTICOS
        if not contrato.imovel or not contrato.proprietario:
            print(f"ERRO CRÍTICO REPASSE: Transação #{transacao_receita.id} de Contrato {contrato.id} incompleto (falta Imóvel ou Proprietário). Repasse abortado.")
            return
        
        # 3. CÁLCULO
        try:
            taxa_percentual = contrato.taxa_administracao_percentual
            valor_comissao = transacao_receita.valor * (taxa_percentual / Decimal(100))
            valor_repasse = transacao_receita.valor - valor_comissao
        except Exception as e:
            print(f"ERRO CRÍTICO REPASSE: Falha no cálculo. Contrato ID: {contrato.id}. Erro: {e}. Repasse abortado.")
            return
        
        # 4. CATEGORIA (Cria a categoria se ela não existir)
        try:
            categoria_repasse, created = Categoria.objects.get_or_create(
                imobiliaria=transacao_receita.imobiliaria,
                nome='Repasse de Aluguel',
                tipo='DESPESA'
            )
            if created:
                print(f"AVISO REPASSE: Categoria 'Repasse de Aluguel' criada automaticamente para o tenant {transacao_receita.imobiliaria.nome}.")
        except Exception as e:
            print(f"ERRO CRÍTICO REPASSE: Falha fatal ao obter/criar Categoria. Erro: {e}. Repasse abortado.")
            return
            
        # 5. DATAS - Tratamento da data de pagamento
        if data_pagamento_receita and isinstance(data_pagamento_receita, date):
            data_base = data_pagamento_receita
        else:
            data_base = timezone.now().date()
            print(f"AVISO REPASSE: data_pagamento_receita era inválida ({data_pagamento_receita}). Usando data atual.")

        data_vencimento_repasse = data_base + timedelta(days=5)
        
        # 6. DESCRIÇÃO SEGURA
        imovel_logradouro = getattr(transacao_receita.imovel, 'logradouro', 'Imóvel Desconhecido')
        mes_referencia = transacao_receita.data_vencimento.strftime('%m/%Y')

        # 7. CRIAÇÃO 
        Transacao.objects.create(
            imobiliaria=transacao_receita.imobiliaria,
            descricao=f"Repasse Aluguel: {imovel_logradouro} (Ref: {mes_referencia})",
            valor=valor_repasse,
            tipo='DESPESA',
            status='PENDENTE',
            data_transacao=data_base, 
            data_vencimento=data_vencimento_repasse,
            
            categoria=categoria_repasse,
            cliente=contrato.proprietario,
            imovel=transacao_receita.imovel,
            contrato=contrato,
            transacao_origem=transacao_receita,
            
            observacoes=f"Repasse gerado automaticamente. Comissão de {taxa_percentual}% (R$ {valor_comissao.quantize(Decimal('0.01'))}) retida."
        )
        print(f"SUCESSO REPASSE: Criada Despesa para Proprietário {contrato.proprietario.nome} de R$ {valor_repasse.quantize(Decimal('0.01'))}. Vencimento: {data_vencimento_repasse}.")

    @action(detail=False, methods=['get'], url_path='a-receber')
    def a_receber(self, request):
        queryset = self.get_queryset().filter(tipo='RECEITA')

        # --- LÓGICA DE FILTRO POR CLIENTE/DOCUMENTO (Corrigida) ---
        cliente_search = request.query_params.get('cliente_search')
        cliente_id_from_search = None
        
        if cliente_search:
            cliente_match = None 
            
            documento_limpo = apenas_numeros(cliente_search)
            
            if len(documento_limpo) >= 11: 
                cliente_match = Cliente.objects.filter(
                    documento=documento_limpo,
                    imobiliaria=self.request.tenant
                ).first()
            
            if not cliente_match:
                cliente_match = Cliente.objects.filter(
                    Q(nome__icontains=cliente_search) | Q(razao_social__icontains=cliente_search),
                    imobiliaria=self.request.tenant
                ).first()
            
            if cliente_match:
                cliente_id_from_search = cliente_match.id
            else:
                return Response(TransacaoListSerializer(queryset.none(), many=True).data)

        cliente_id_final = request.query_params.get('cliente_id') or cliente_id_from_search
        
        if cliente_id_final:
            queryset = queryset.filter(Q(cliente_id=cliente_id_final) | Q(contrato__inquilino_id=cliente_id_final))
        # --- FIM DA LÓGICA DE FILTRO ---
        
        status_filter = request.query_params.get('status')
        if status_filter and status_filter.upper() in ['PENDENTE', 'PAGO', 'ATRASADO']:
            queryset = queryset.filter(status=status_filter.upper())

        data_vencimento_inicio = request.query_params.get('data_vencimento_inicio')
        data_vencimento_fim = request.query_params.get('data_vencimento_fim')
        if data_vencimento_inicio and data_vencimento_fim:
            start_date = parse_date(data_vencimento_inicio)
            end_date = parse_date(data_vencimento_fim)
            if start_date and end_date:
                queryset = queryset.filter(data_vencimento__range=[start_date, end_date])
                
        queryset = queryset.order_by('data_vencimento') 
        
        serializer = TransacaoListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='a-pagar')
    def a_pagar(self, request):
        queryset = self.get_queryset().filter(tipo='DESPESA')

        # --- INÍCIO DA LÓGICA DE FILTRO POR CLIENTE/DOCUMENTO (PARA "A PAGAR") ---
        cliente_search = request.query_params.get('cliente_search')
        cliente_id_from_search = None
        
        if cliente_search:
            cliente_match = None 
            
            documento_limpo = apenas_numeros(cliente_search)
            
            if len(documento_limpo) >= 11: 
                cliente_match = Cliente.objects.filter(
                    documento=documento_limpo,
                    imobiliaria=self.request.tenant
                ).first()
            
            if not cliente_match:
                cliente_match = Cliente.objects.filter(
                    Q(nome__icontains=cliente_search) | Q(razao_social__icontains=cliente_search),
                    imobiliaria=self.request.tenant
                ).first()
            
            if cliente_match:
                cliente_id_from_search = cliente_match.id
            else:
                return Response(TransacaoListSerializer(queryset.none(), many=True).data)

        cliente_id_final = request.query_params.get('cliente_id') or cliente_id_from_search
        
        if cliente_id_final:
            # Para "A Pagar", o cliente pode ser o recebedor (cliente) ou o proprietário (no contrato)
            queryset = queryset.filter(Q(cliente_id=cliente_id_final) | Q(contrato__proprietario_id=cliente_id_final))
        # --- FIM DA LÓGICA DE FILTRO ---
        
        status_filter = request.query_params.get('status')
        if status_filter and status_filter.upper() in ['PENDENTE', 'PAGO', 'ATRASADO']:
            queryset = queryset.filter(status=status_filter.upper())

        data_vencimento_inicio = request.query_params.get('data_vencimento_inicio')
        data_vencimento_fim = request.query_params.get('data_vencimento_fim')
        if data_vencimento_inicio and data_vencimento_fim:
            start_date = parse_date(data_vencimento_inicio)
            end_date = parse_date(data_vencimento_fim)
            if start_date and end_date:
                queryset = queryset.filter(data_vencimento__range=[start_date, end_date])
                
        queryset = queryset.order_by('data_vencimento') 
        
        serializer = TransacaoListSerializer(queryset, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        aggregates = queryset.aggregate(
            a_receber_pendente=Sum(
                Case(
                    When(tipo='RECEITA', status__in=['PENDENTE', 'ATRASADO'], then='valor'),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            a_receber_pago_mes=Sum(
                Case(
                    When(
                        tipo='RECEITA', 
                        status='PAGO', 
                        data_pagamento__month=today.month, 
                        data_pagamento__year=today.year,   
                        then='valor'
                    ),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            a_pagar_pendente=Sum(
                Case(
                    When(tipo='DESPESA', status__in=['PENDENTE', 'ATRASADO'], then='valor'),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            a_pagar_pago_mes=Sum(
                Case(
                    When(
                        tipo='DESPESA', 
                        status='PAGO', 
                        data_pagamento__month=today.month, 
                        data_pagamento__year=today.year,   
                        then='valor'
                    ),
                    default=0,
                    output_field=DecimalField()
                )
            )
        )

        stats_data = {
            'a_receber': {
                'pendente': aggregates['a_receber_pendente'] or 0,
                'pago_mes_atual': aggregates['a_receber_pago_mes'] or 0
            },
            'a_pagar': {
                'pendente': aggregates['a_pagar_pendente'] or 0,
                'pago_mes_atual': aggregates['a_pagar_pago_mes'] or 0
            },
            'saldo_previsto': (aggregates['a_receber_pendente'] or 0) - (aggregates['a_pagar_pendente'] or 0)
        }
        return Response(stats_data)

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
        
        queryset = Transacao.objects.filter(
            imobiliaria=request.tenant, 
            data_pagamento__range=[start_date, end_date], 
            status='PAGO'
        )
        
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
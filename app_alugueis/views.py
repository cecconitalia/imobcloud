# C:\wamp64\www\imobcloud\app_alugueis\views.py

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, Case, When, Value, CharField, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal # Importado Decimal

from .models import Aluguel
from .serializers import AluguelSerializer
from app_contratos.models import Contrato, Pagamento 
from app_financeiro.models import Transacao # Importado Transacao

class AluguelViewSet(viewsets.ModelViewSet):
    queryset = Aluguel.objects.all()
    serializer_class = AluguelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Aluguel.objects.all()
        if hasattr(user, 'imobiliaria') and user.imobiliaria:
            return Aluguel.objects.filter(contrato__imobiliaria=user.imobiliaria)
        return Aluguel.objects.none()

class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        if not tenant:
            return Response({"error": "Imobiliária não encontrada."}, status=400)

        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)
        
        # Calcula o último dia do mês atual
        if hoje.month == 12:
            fim_mes = hoje.replace(day=31)
        else:
            fim_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)

        # 1. Obter contratos de aluguel ativos
        contratos_ativos = Contrato.objects.filter(
            imobiliaria=tenant, 
            status_contrato='ATIVO', 
            tipo_contrato='ALUGUEL'
        )

        # 2. Calcular Total de Contratos Ativos
        total_contratos_ativos = contratos_ativos.count()
        
        # 3. Aluguéis Pendentes (a vencer) no MÊS ATUAL
        alugueis_a_vencer = Pagamento.objects.filter(
            contrato__in=contratos_ativos,
            data_vencimento__gte=inicio_mes,
            data_vencimento__lte=fim_mes,
            status='PENDENTE'
        ).count()
        
        # 4. Calcular Valor Recebido (Transações PAGAS no Mês Atual)
        # SOMA O VALOR E CONVERTE PARA FLOAT para evitar erro de serialização do JSON
        valor_recebido_mes = Transacao.objects.filter(
            imobiliaria=tenant,
            tipo='RECEITA',
            contrato__tipo_contrato='ALUGUEL',
            status='PAGO',
            data_pagamento__gte=inicio_mes,
            data_pagamento__lte=fim_mes
        ).aggregate(Sum('valor'))['valor__sum']
        
        # Garante que seja float(0) se for None
        valor_recebido_mes = float(valor_recebido_mes) if valor_recebido_mes is not None else 0.0

        # 5. Aluguéis Atrasados (Pagamentos com status ATRASADO)
        alugueis_atrasados = Pagamento.objects.filter(
            contrato__in=contratos_ativos,
            status='ATRASADO'
        ).count()

        # 6. Próximos vencimentos (Próximos 7 dias)
        proximos_vencimentos = Pagamento.objects.filter(
            contrato__in=contratos_ativos,
            data_vencimento__gte=hoje,
            data_vencimento__lte=hoje + timedelta(days=7),
            status__in=['PENDENTE', 'ATRASADO']
        ).annotate(
            inquilino_nome=Case(
                When(contrato__inquilino__tipo_pessoa='JURIDICA', then=F('contrato__inquilino__razao_social')),
                default=F('contrato__inquilino__nome'),
                output_field=CharField()
            ),
            proprietario_nome=Case(
                When(contrato__proprietario__tipo_pessoa='JURIDICA', then=F('contrato__proprietario__razao_social')),
                default=F('contrato__proprietario__nome'),
                output_field=CharField()
            ),
            imovel_titulo=F('contrato__imovel__titulo_anuncio')
        ).values(
            'id', 'data_vencimento', 'valor', 'status',
            'inquilino_nome', 'proprietario_nome', 'imovel_titulo'
        ).order_by('data_vencimento')

        data = {
            'contratos_ativos': total_contratos_ativos,
            'alugueis_a_vencer': alugueis_a_vencer,
            'alugueis_atrasados': alugueis_atrasados,
            'valor_recebido_mes': valor_recebido_mes, # Agora é um float
            'proximos_alugueis': list(proximos_vencimentos)
        }

        return Response(data)
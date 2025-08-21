# C:\wamp64\www\ImobCloud\app_alugueis\views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, F # CORREÇÃO: F foi adicionado aqui
from django.utils import timezone
from datetime import timedelta
from app_contratos.models import Contrato, Pagamento

class AluguelDashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        imobiliaria = request.tenant

        # 1. Contratos de Aluguel Ativos
        contratos_ativos = Contrato.objects.filter(
            imobiliaria=imobiliaria,
            tipo_contrato='Aluguel',
            status_contrato='Ativo'
        ).count()

        # 2. Aluguéis a Vencer (Próximos 7 dias)
        hoje = timezone.now().date()
        proximos_7_dias = hoje + timedelta(days=7)
        alugueis_a_vencer = Pagamento.objects.filter(
            contrato__imobiliaria=imobiliaria,
            contrato__tipo_contrato='Aluguel',
            status='PENDENTE',
            data_vencimento__gte=hoje,
            data_vencimento__lte=proximos_7_dias
        ).annotate(
            imovel_titulo=F('contrato__imovel__titulo_anuncio'),
            inquilino_nome=F('contrato__inquilino__nome_completo')
        ).values(
            'id', 'imovel_titulo', 'inquilino_nome', 'data_vencimento', 'valor'
        ).order_by('data_vencimento')

        # 3. Aluguéis Atrasados
        alugueis_atrasados = Pagamento.objects.filter(
            contrato__imobiliaria=imobiliaria,
            contrato__tipo_contrato='Aluguel',
            status='PENDENTE',
            data_vencimento__lt=hoje
        ).count()

        # 4. Valor Recebido no Mês Atual
        primeiro_dia_mes = hoje.replace(day=1)
        valor_recebido_mes = Pagamento.objects.filter(
            contrato__imobiliaria=imobiliaria,
            contrato__tipo_contrato='Aluguel',
            status='PAGO',
            data_pagamento__gte=primeiro_dia_mes
        ).aggregate(total=Sum('valor'))['total'] or 0

        data = {
            'contratos_ativos': contratos_ativos,
            'alugueis_a_vencer': list(alugueis_a_vencer),
            'alugueis_atrasados': alugueis_atrasados,
            'valor_recebido_mes': valor_recebido_mes,
        }
        
        return Response(data)
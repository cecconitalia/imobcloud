# C:\wamp64\www\imobcloud\app_alugueis\views.py

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, Case, When, Value, CharField, F
from django.utils import timezone
from datetime import timedelta

from .models import Aluguel
from .serializers import AluguelSerializer
from app_contratos.models import Contrato, Pagamento # ADICIONADO: Importar o modelo Pagamento

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
        fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        # 1. Obter contratos de aluguel ativos
        contratos_ativos = Contrato.objects.filter(
            imobiliaria=tenant, 
            status_contrato='ATIVO', 
            tipo_contrato='ALUGUEL'
        )

        # 2. Calcular estatísticas gerais a partir dos contratos
        total_contratos_ativos = contratos_ativos.count()
        valor_total_alugueis_ativos = contratos_ativos.aggregate(Sum('valor_total'))['valor_total__sum'] or 0

        # 3. CORRIGIDO: Consultar o modelo Pagamento para obter pendências
        pagamentos_pendentes_mes = Pagamento.objects.filter(
            contrato__in=contratos_ativos,
            data_vencimento__gte=inicio_mes,
            data_vencimento__lte=fim_mes,
            status='PENDENTE'
        ).count()

        # 4. CORRIGIDO: Consultar o modelo Pagamento para obter próximos vencimentos
        proximos_vencimentos = Pagamento.objects.filter(
            contrato__in=contratos_ativos,
            data_vencimento__gte=hoje,
            data_vencimento__lte=hoje + timedelta(days=7),
            status='PENDENTE'
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
            'total_contratos_ativos': total_contratos_ativos,
            'valor_total_alugueis_ativos': valor_total_alugueis_ativos,
            'alugueis_pendentes_mes': pagamentos_pendentes_mes, # Nome da variável atualizado para clareza
            'proximos_vencimentos': list(proximos_vencimentos)
        }

        return Response(data)
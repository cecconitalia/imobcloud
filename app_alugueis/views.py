from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, Case, When, Value, CharField, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal 

from core.models import Imobiliaria
from .models import Aluguel
from .serializers import AluguelSerializer
from app_contratos.models import Contrato, Pagamento 
from app_financeiro.models import Transacao 

# --- VIEWSET PADRÃO ---
class AluguelViewSet(viewsets.ModelViewSet):
    queryset = Aluguel.objects.all()
    serializer_class = AluguelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        tenant = getattr(self.request, 'tenant', None)
        
        # Fallback para usuário logado
        if not tenant and hasattr(user, 'imobiliaria'):
            tenant = user.imobiliaria

        if user.is_superuser:
            if not tenant:
                return Aluguel.objects.all()
            return Aluguel.objects.filter(contrato__imobiliaria=tenant)
        
        if tenant:
            return Aluguel.objects.filter(contrato__imobiliaria=tenant)
            
        return Aluguel.objects.none()

# --- VIEW DO DASHBOARD (AQUI ESTÁ A CORREÇÃO) ---
class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        print(f"DEBUG: Iniciando DashboardStats para usuário {request.user}")

        # 1. Tenta pegar pelo Middleware
        tenant = getattr(request, 'tenant', None)
        print(f"DEBUG: 1. Tenant do Middleware: {tenant}")
        
        # 2. Tenta pegar pelo Perfil do Usuário
        if not tenant:
            if hasattr(request.user, 'imobiliaria') and request.user.imobiliaria:
                tenant = request.user.imobiliaria
                print(f"DEBUG: 2. Tenant do Usuário: {tenant}")
            else:
                print("DEBUG: 2. Usuário sem imobiliária vinculada.")

        # 3. Tenta forçar a imobiliária 'imobhome' (Específico para o seu caso)
        if not tenant:
            tenant = Imobiliaria.objects.filter(subdominio='imobhome').first()
            print(f"DEBUG: 3. Tenant forçado por subdomínio 'imobhome': {tenant}")

        # 4. Último recurso para Superusuário: Pega a primeira que existir
        if not tenant and request.user.is_superuser:
            tenant = Imobiliaria.objects.first()
            print(f"DEBUG: 4. Tenant fallback (primeiro do banco): {tenant}")

        # --- BLOQUEIO FINAL ---
        if not tenant:
            # Lista as imobiliárias existentes para ajudar a debugar
            total_imobs = Imobiliaria.objects.count()
            msg = f"Imobiliária não encontrada. Total no banco: {total_imobs}."
            print(f"ERRO CRÍTICO: {msg}")
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        # --- LÓGICA DO DASHBOARD ---
        try:
            hoje = timezone.now().date()
            inicio_mes = hoje.replace(day=1)
            
            if hoje.month == 12:
                fim_mes = hoje.replace(day=31)
            else:
                fim_mes = hoje.replace(month=hoje.month + 1, day=1) - timedelta(days=1)

            # Filtros
            contratos_ativos = Contrato.objects.filter(
                imobiliaria=tenant, 
                status_contrato='ATIVO', 
                tipo_contrato='ALUGUEL'
            )
            total_contratos_ativos = contratos_ativos.count()
            
            alugueis_a_vencer = Pagamento.objects.filter(
                contrato__in=contratos_ativos,
                data_vencimento__gte=inicio_mes,
                data_vencimento__lte=fim_mes,
                status='PENDENTE'
            ).count()
            
            valor_recebido = Transacao.objects.filter(
                imobiliaria=tenant,
                tipo='RECEITA',
                contrato__tipo_contrato='ALUGUEL',
                status='PAGO',
                data_pagamento__gte=inicio_mes,
                data_pagamento__lte=fim_mes
            ).aggregate(Sum('valor'))['valor__sum']
            
            valor_recebido_mes = float(valor_recebido) if valor_recebido else 0.0

            alugueis_atrasados = Pagamento.objects.filter(
                contrato__in=contratos_ativos,
                status='ATRASADO'
            ).count()

            proximos_vencimentos_qs = Pagamento.objects.filter(
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

            proximos_vencimentos = []
            for item in proximos_vencimentos_qs:
                item['valor'] = float(item['valor']) if item['valor'] else 0.0
                proximos_vencimentos.append(item)

            data = {
                'contratos_ativos': total_contratos_ativos,
                'alugueis_a_vencer': alugueis_a_vencer,
                'alugueis_atrasados': alugueis_atrasados,
                'valor_recebido_mes': valor_recebido_mes,
                'proximos_alugueis': proximos_vencimentos
            }

            return Response(data)

        except Exception as e:
            import traceback
            print(f"ERRO INTERNO NO DASHBOARD: {e}")
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)
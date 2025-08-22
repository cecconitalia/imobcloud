# C:\wamp64\www\ImobCloud\app_contratos\views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework import filters
from django.shortcuts import get_object_or_404
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from core.models import PerfilUsuario, Imobiliaria
from .models import Contrato, Pagamento
from .serializers import (
    ContratoListSerializer,
    ContratoDetailSerializer,
    ContratoWriteSerializer,
    PagamentoSerializer
)
from dateutil.relativedelta import relativedelta
from rest_framework.views import APIView
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.decorators import action

from app_financeiro.models import Transacao, Categoria, ContaBancaria
from django.db import transaction
from decimal import Decimal
from django.db.models import F

def get_categoria_aluguel(imobiliaria: Imobiliaria) -> Categoria:
    categoria, _ = Categoria.objects.get_or_create(
        imobiliaria=imobiliaria,
        nome='Receita de Aluguel',
        defaults={'tipo': 'RECEITA'}
    )
    return categoria

def get_conta_bancaria_padrao(imobiliaria: Imobiliaria) -> ContaBancaria:
    conta = ContaBancaria.objects.filter(imobiliaria=imobiliaria, ativo=True).first()
    if not conta:
        raise ValidationError(f"Nenhuma conta bancária ativa encontrada para a imobiliária {imobiliaria.nome}. Por favor, cadastre e ative uma conta em Financeiro > Gerir Contas antes de criar um contrato de aluguel.")
    return conta

class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['imovel__endereco', 'inquilino__nome_completo', 'informacoes_adicionais']

    def get_serializer_class(self):
        if self.action == 'list':
            return ContratoListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ContratoWriteSerializer
        return ContratoDetailSerializer

    def get_queryset(self):
        base_queryset = Contrato.objects.exclude(status_contrato='Inativo')
        if self.request.user.is_superuser:
            return base_queryset.all()
        elif self.request.tenant:
            return base_queryset.filter(imobiliaria=self.request.tenant)
        return Contrato.objects.none()
    
    def _gerar_pagamentos_aluguel(self, contrato: Contrato):
        if contrato.tipo_contrato != 'Aluguel' or not contrato.duracao_meses:
            return

        if Pagamento.objects.filter(contrato=contrato).exists():
            return
        
        valor_parcela = contrato.valor_total
        if not valor_parcela or valor_parcela <= 0:
            return

        try:
            categoria = get_categoria_aluguel(contrato.imobiliaria)
            conta_bancaria = get_conta_bancaria_padrao(contrato.imobiliaria)

            for i in range(contrato.duracao_meses):
                data_vencimento = contrato.data_inicio + relativedelta(months=i)
                Pagamento.objects.create(
                    contrato=contrato,
                    valor=valor_parcela,
                    data_vencimento=data_vencimento,
                    status='PENDENTE',
                )
                Transacao.objects.create(
                    imobiliaria=contrato.imobiliaria,
                    contrato=contrato,
                    imovel=contrato.imovel,
                    tipo='RECEITA',
                    descricao=f"Aluguel: {contrato.imovel.titulo_anuncio} ({i+1}/{contrato.duracao_meses})",
                    valor=valor_parcela,
                    data_vencimento=data_vencimento,
                    status='PENDENTE',
                    categoria=categoria,
                    conta_bancaria=conta_bancaria
                )
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError("Ocorreu um erro inesperado ao gerar as parcelas financeiras.")

    # ==========================================================================================
    # <<< LÓGICA DE CRIAÇÃO E ATUALIZAÇÃO DEFINITIVAMENTE CORRIGIDA >>>
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Separa os dados ManyToMany
        formas_pagamento_data = serializer.validated_data.pop('formas_pagamento', [])
        
        # Adiciona a imobiliária aos dados restantes
        validated_data = serializer.validated_data
        validated_data['imobiliaria'] = self.request.tenant

        # Cria o objeto Contrato manualmente
        contrato = Contrato.objects.create(**validated_data)
        
        # Associa os dados ManyToMany
        if formas_pagamento_data:
            contrato.formas_pagamento.set(formas_pagamento_data)
        
        # Gera as parcelas
        self._gerar_pagamentos_aluguel(contrato)
        
        headers = self.get_success_headers(serializer.data)
        return Response(ContratoDetailSerializer(contrato).data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    def perform_update(self, serializer):
        formas_pagamento_data = serializer.validated_data.pop('formas_pagamento', None)

        contrato = serializer.save()

        if formas_pagamento_data is not None:
            contrato.formas_pagamento.set(formas_pagamento_data)

        if contrato.tipo_contrato == 'Aluguel' and contrato.status_contrato == 'Ativo':
             self._gerar_pagamentos_aluguel(contrato)
    # ==========================================================================================

    def perform_destroy(self, instance):
        if self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and instance.imobiliaria == self.request.tenant and self.request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN):
            instance.status_contrato = 'Inativo'
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied("Você não tem permissão para inativar este contrato.")
    
    @action(detail=True, methods=['get'])
    def pagamentos(self, request, pk=None):
        contrato = self.get_object()
        pagamentos = contrato.pagamentos.all()
        serializer = PagamentoSerializer(pagamentos, many=True)
        return Response(serializer.data)

class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Pagamento.objects.all()
        elif self.request.tenant:
            return Pagamento.objects.filter(contrato__imobiliaria=self.request.tenant)
        return Pagamento.objects.none()

class GerarReciboView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pagamento_id, *args, **kwargs):
        pagamento = get_object_or_404(Pagamento, pk=pagamento_id)
        user = request.user
        if not user.is_superuser and pagamento.contrato.imobiliaria != self.request.tenant:
            raise PermissionDenied("Você não tem permissão para gerar este recibo.")
        if pagamento.contrato.tipo_contrato != 'Aluguel':
             return HttpResponse("Este contrato não é de aluguel.", status=400)
        context = {
            'pagamento': pagamento,
            'contrato': pagamento.contrato,
            'cliente': pagamento.contrato.inquilino,
            'imovel': pagamento.contrato.imovel,
            'imobiliaria': pagamento.contrato.imobiliaria,
            'data_emissao': timezone.now().date(),
        }
        html_string = render_to_string('recibo_template.html', context)
        return HttpResponse(html_string)
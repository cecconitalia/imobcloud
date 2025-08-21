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

# NOVAS IMPORTAÇÕES PARA AUTOMATIZAR PAGAMENTOS
from app_financeiro.models import Transacao, Categoria, ContaBancaria
from django.db import transaction
from decimal import Decimal
from django.db.models import F


# Helper para encontrar a categoria padrão de aluguéis
def get_categoria_aluguel(imobiliaria: Imobiliaria) -> Categoria:
    categoria, _ = Categoria.objects.get_or_create(
        imobiliaria=imobiliaria,
        nome='Receita de Aluguel',
        defaults={'tipo': 'RECEITA'}
    )
    return categoria

# Helper para encontrar uma conta bancária padrão
def get_conta_bancaria_padrao(imobiliaria: Imobiliaria) -> ContaBancaria:
    conta = ContaBancaria.objects.filter(imobiliaria=imobiliaria, ativo=True).first()
    if not conta:
        raise PermissionDenied(f"Nenhuma conta bancária ativa encontrada para {imobiliaria.nome}.")
    return conta


class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['imovel__endereco', 'inquilino__nome_completo', 'condicoes_pagamento']

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
            print(f"AVISO: Pagamentos para o contrato {contrato.id} já existem. Pulando a criação.")
            return
        
        # CORREÇÃO CRUCIAL: Usar o valor do contrato para a parcela
        valor_parcela = contrato.valor_total
        if not valor_parcela or valor_parcela <= 0:
            print(f"AVISO: Contrato {contrato.id} de aluguel sem valor total definido ou com valor zero. Pagamentos não criados.")
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
            print(f"SUCESSO: {contrato.duracao_meses} pagamentos de aluguel criados para o contrato {contrato.id}.")

        except PermissionDenied as e:
            print(f"ERRO: Falha ao gerar pagamentos para o contrato {contrato.id}: {e}")
        except Exception as e:
            print(f"ERRO: Erro inesperado ao gerar pagamentos para o contrato {contrato.id}: {e}")

    @transaction.atomic
    def perform_create(self, serializer):
        imovel = serializer.validated_data.get('imovel')
        inquilino = serializer.validated_data.get('inquilino')
        proprietario = serializer.validated_data.get('proprietario')
        
        if serializer.validated_data.get('tipo_contrato') == 'Aluguel' and not (inquilino and proprietario):
             raise ValidationError("Para contratos de Aluguel, 'Inquilino' e 'Proprietário' são obrigatórios.")

        if not self.request.user.is_superuser:
            if not (hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR]):
                raise PermissionDenied("Você não tem permissão para criar contratos.")
            
            if imovel.imobiliaria != self.request.tenant:
                raise PermissionDenied("Não é permitido criar contratos com imóveis de outra imobiliária.")
            if inquilino and inquilino.imobiliaria != self.request.tenant:
                 raise PermissionDenied("Não é permitido criar contratos com inquilinos de outra imobiliária.")
            if proprietario and proprietario.imobiliaria != self.request.tenant:
                 raise PermissionDenied("Não é permitido criar contratos com proprietários de outra imobiliária.")

        contrato = serializer.save(imobiliaria=self.request.tenant)
        self._gerar_pagamentos_aluguel(contrato)

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            contrato = serializer.save()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and serializer.instance.imobiliaria == self.request.tenant:
            contrato = serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar este contrato.")

        # NOVO: Se o contrato for de aluguel e tiver o status ativo, garanta a criação dos pagamentos.
        if contrato.tipo_contrato == 'Aluguel' and contrato.status_contrato == 'Ativo':
             self._gerar_pagamentos_aluguel(contrato)

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
        try:
            pagamento = get_object_or_404(
                Pagamento.objects.select_related(
                    'contrato__inquilino',
                    'contrato__imovel', 
                    'contrato__imobiliaria'
                ), 
                pk=pagamento_id
            )

            user = request.user
            if not user.is_superuser and pagamento.contrato.imobiliaria != request.tenant:
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

        except Pagamento.DoesNotExist:
            return HttpResponse("Pagamento não encontrado.", status=404)
        except Exception as e:
            return HttpResponse(f"Ocorreu um erro: {e}", status=500)
# C:\wamp64\www\ImobCloud\app_contratos\views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
# ATUALIZADO: PermissionDenied foi movido para rest_framework.exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import filters
from django.shortcuts import get_object_or_404
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from core.models import PerfilUsuario
from .models import Contrato, Pagamento
from .serializers import (
    ContratoListSerializer,
    ContratoDetailSerializer,
    ContratoWriteSerializer,
    PagamentoSerializer
)
from dateutil.relativedelta import relativedelta


class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['imovel__endereco', 'cliente__nome_completo', 'condicoes_pagamento']

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

    def perform_create(self, serializer):
        imovel = serializer.validated_data.get('imovel')
        cliente = serializer.validated_data.get('cliente')
        
        if not self.request.user.is_superuser:
            if not (hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR]):
                raise PermissionDenied("Você não tem permissão para criar contratos.")
            if imovel.imobiliaria != self.request.tenant or cliente.imobiliaria != self.request.tenant:
                raise PermissionDenied("Não é permitido criar contratos com clientes ou imóveis de outra imobiliária.")

        contrato = serializer.save(imobiliaria=self.request.tenant)

        if contrato.tipo_contrato == 'Aluguel' and imovel.valor_aluguel:
            for i in range(12):
                data_vencimento = contrato.data_inicio + relativedelta(months=i)
                Pagamento.objects.create(
                    contrato=contrato,
                    valor=imovel.valor_aluguel,
                    data_vencimento=data_vencimento
                )

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar este contrato.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and instance.imobiliaria == self.request.tenant):
            instance.status_contrato = 'Inativo'
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied("Você não tem permissão para inativar este contrato.")


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
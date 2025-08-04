# C:\wamp64\www\ImobCloud\app_contratos\views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django.shortcuts import get_object_or_404
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from core.models import PerfilUsuario # NOVO: Importamos o PerfilUsuario
from .models import Contrato
from .serializers import ContratoSerializer


class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['imovel__endereco', 'cliente__nome_completo', 'condicoes_pagamento']

    def get_queryset(self):
        base_queryset = Contrato.objects.exclude(status_contrato='Inativo')

        if self.request.user.is_superuser:
            return base_queryset.all()
        elif self.request.tenant:
            return base_queryset.filter(imobiliaria=self.request.tenant)
        return Contrato.objects.none()

    def perform_create(self, serializer):
        # Apenas ADMINs, CORRETORES e superusuários podem criar contratos
        imovel_id = self.request.data.get('imovel')
        cliente_id = self.request.data.get('cliente')
        if self.request.user.is_superuser:
            imovel = get_object_or_404(Imovel, pk=imovel_id)
            cliente = get_object_or_404(Cliente, pk=cliente_id)
            if 'imobiliaria' in self.request.data:
                imobiliaria_obj = get_object_or_404(self.request.tenant._meta.model, pk=self.request.data['imobiliaria'])
                serializer.save(imobiliaria=imobiliaria_obj, imovel=imovel, cliente=cliente)
            else:
                # Corrigido para superusuários, que devem sempre especificar a imobiliária
                raise Exception("Para superusuário, a imobiliária é obrigatória.")
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR]:
            imovel_id = self.request.data.get('imovel')
            cliente_id = self.request.data.get('cliente')
            imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)
            cliente = get_object_or_404(Cliente, pk=cliente_id, imobiliaria=self.request.tenant)
            serializer.save(imobiliaria=self.request.tenant, imovel=imovel, cliente=cliente)
        else:
            raise Exception("Não foi possível associar o contrato. Tenant não identificado ou inválido.")

    def perform_update(self, serializer):
        # Apenas ADMINs, CORRETORES e superusuários podem atualizar contratos
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este contrato.")

    def perform_destroy(self, instance):
        # Apenas ADMINs e superusuários podem inativar contratos
        if self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and instance.imobiliaria == self.request.tenant):
            instance.status_contrato = 'Inativo'
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise Exception("Você não tem permissão para inativar este contrato.")
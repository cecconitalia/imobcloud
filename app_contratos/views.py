# C:\wamp64\www\ImobCloud\app_contratos\views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# 1. IMPORTAR O MÓDULO DE FILTROS
from rest_framework import filters

from .models import Contrato
from .serializers import ContratoSerializer
from django.shortcuts import get_object_or_404
from app_imoveis.models import Imovel 
from app_clientes.models import Cliente

class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

    # 2. ADICIONAR OS BACKENDS DE FILTRO E PESQUISA
    filter_backends = [filters.SearchFilter]
    
    # 3. DEFINIR OS CAMPOS ONDE A PESQUISA IRÁ PROCURAR
    # Nota: Usamos '__' para pesquisar em campos de modelos relacionados.
    search_fields = ['imovel__endereco', 'cliente__nome_completo', 'condicoes_pagamento']


    def get_queryset(self):
        # A sua lógica de queryset existente, que já filtra por status, permanece igual.
        # O Django REST Framework aplicará a pesquisa sobre o resultado desta função.
        base_queryset = Contrato.objects.exclude(status_contrato='Inativo')

        if self.request.user.is_superuser:
            return base_queryset.all()
        elif self.request.tenant:
            return base_queryset.filter(imobiliaria=self.request.tenant)
        return Contrato.objects.none()

    def perform_create(self, serializer):
        # Nenhuma alteração aqui. A criação de contratos continua a funcionar como antes.
        imovel_id = self.request.data.get('imovel')
        cliente_id = self.request.data.get('cliente')
        if self.request.user.is_superuser:
            imovel = get_object_or_404(Imovel, pk=imovel_id)
            cliente = get_object_or_404(Cliente, pk=cliente_id)
            if 'imobiliaria' in self.request.data:
                imobiliaria_obj = get_object_or_404(self.request.tenant._meta.model, pk=self.request.data['imobiliaria'])
                serializer.save(imobiliaria=imobiliaria_obj, imovel=imovel, cliente=cliente)
            else:
                serializer.save(imobiliaria=self.request.tenant, imovel=imovel, cliente=cliente)
        elif self.request.tenant:
            imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)
            cliente = get_object_or_404(Cliente, pk=cliente_id, imobiliaria=self.request.tenant)
            serializer.save(imobiliaria=self.request.tenant, imovel=imovel, cliente=cliente)
        else:
            raise Exception("Não foi possível associar o contrato. Tenant não identificado ou inválido.")

    def perform_update(self, serializer):
        # Nenhuma alteração aqui. A edição de contratos continua a funcionar como antes.
        if self.request.user.is_superuser:
            serializer.save()
        elif serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este contrato.")

    def perform_destroy(self, instance):
        # Lógica de inativação (soft delete) adicionada anteriormente. Nenhuma alteração aqui.
        if self.request.user.is_superuser or instance.imobiliaria == self.request.tenant:
            instance.status_contrato = 'Inativo'
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise Exception("Você não tem permissão para inativar este contrato.")
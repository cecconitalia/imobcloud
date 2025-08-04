# C:\wamp64\www\ImobCloud\app_clientes\views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

# 1. IMPORTAR O MÓDULO DE FILTROS
from rest_framework import filters

from .models import Cliente, Visita
from .serializers import ClienteSerializer, VisitaSerializer
from app_imoveis.models import Imovel 

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    # 2. ADICIONAR OS BACKENDS DE FILTRO E PESQUISA
    filter_backends = [filters.SearchFilter]
    
    # 3. DEFINIR OS CAMPOS ONDE A PESQUISA IRÁ PROCURAR
    search_fields = ['nome_completo', 'cpf_cnpj', 'email']


    def get_queryset(self):
        # A sua lógica de queryset existente, que já filtra por clientes ativos, permanece igual.
        # O Django REST Framework aplicará a pesquisa sobre o resultado desta função.
        base_queryset = Cliente.objects.filter(ativo=True)

        if self.request.user.is_superuser:
            return base_queryset.all()
        elif self.request.tenant:
            return base_queryset.filter(imobiliaria=self.request.tenant)
        return Cliente.objects.none()

    def perform_create(self, serializer):
        # Nenhuma alteração aqui. A criação de clientes continua a funcionar como antes.
        if self.request.user.is_superuser and 'imobiliaria' in self.request.data:
            imobiliaria_id = self.request.data['imobiliaria']
            imobiliaria_obj = get_object_or_404(self.request.tenant._meta.model, pk=imobiliaria_id)
            serializer.save(imobiliaria=imobiliaria_obj)
        elif self.request.tenant:
            serializer.save(imobiliaria=self.request.tenant)
        else:
            raise Exception("Não foi possível associar o cliente a uma imobiliária. Tenant não identificado.")

    def perform_update(self, serializer):
        # Nenhuma alteração aqui. A edição de clientes continua a funcionar como antes.
        if self.request.user.is_superuser:
            serializer.save()
        elif serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este cliente.")

    def perform_destroy(self, instance):
        # Lógica de inativação (soft delete) adicionada anteriormente. Nenhuma alteração aqui.
        if self.request.user.is_superuser or instance.imobiliaria == self.request.tenant:
            instance.ativo = False
            instance.save()
        else:
            raise Exception("Você não tem permissão para inativar este cliente.")


# A ViewSet de Visitas permanece completamente sem alterações.
class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all()
    serializer_class = VisitaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Visita.objects.all()
        elif self.request.tenant:
            return Visita.objects.filter(imobiliaria=self.request.tenant)
        return Visita.objects.none()

    def perform_create(self, serializer):
        imovel_id = self.request.data.get('imovel')
        cliente_id = self.request.data.get('cliente')
        if self.request.user.is_superuser:
            imovel = get_object_or_404(Imovel, pk=imovel_id)
            cliente = get_object_or_404(Cliente, pk=cliente_id)
            if 'imobiliaria' in self.request.data:
                imobiliaria_obj = get_object_or_404(self.request.tenant._meta.model, pk=self.request.data['imobiliaria'])
                serializer.save(imobiliaria=imobiliaria_obj, cliente=cliente, imovel=imovel)
            else:
                serializer.save(imobiliaria=self.request.tenant, cliente=cliente, imovel=imovel)
        elif self.request.tenant:
            imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)
            cliente = get_object_or_404(Cliente, pk=cliente_id, imobiliaria=self.request.tenant)
            serializer.save(imobiliaria=self.request.tenant, cliente=cliente, imovel=imovel)
        else:
            raise Exception("Não foi possível associar a visita. Tenant não identificado ou inválido.")

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar esta visita.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser:
            instance.delete()
        elif instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir esta visita.")
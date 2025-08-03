# C:\wamp64\www\ImobCloud\app_clientes\views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Cliente, Visita
from .serializers import ClienteSerializer, VisitaSerializer
from django.shortcuts import get_object_or_404

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all() # Necessário para o router
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.tenant:
            return Cliente.objects.filter(imobiliaria=self.request.tenant)
        return Cliente.objects.none()

    def perform_create(self, serializer):
        if self.request.tenant:
            serializer.save(imobiliaria=self.request.tenant)
        else:
            raise Exception("Não foi possível associar o cliente a uma imobiliária. Tenant não identificado.")

    def perform_update(self, serializer):
        if serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este cliente.")

    def perform_destroy(self, instance):
        if instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir este cliente.")

class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all() # Necessário para o router
    serializer_class = VisitaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.tenant:
            return Visita.objects.filter(imobiliaria=self.request.tenant)
        return Visita.objects.none()

    def perform_create(self, serializer):
        # Ao criar uma visita, garanta que o cliente e imóvel associados pertencem ao tenant atual
        cliente_id = self.request.data.get('cliente')
        imovel_id = self.request.data.get('imovel')
        
        cliente = get_object_or_404(Cliente, pk=cliente_id, imobiliaria=self.request.tenant)
        # Importante: O Imovel também precisa ser do tenant atual. Se não for, dará erro.
        # Você precisaria importar Imovel de app_imoveis.models
        from app_imoveis.models import Imovel 
        imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)

        serializer.save(imobiliaria=self.request.tenant, cliente=cliente, imovel=imovel)

    def perform_update(self, serializer):
        if serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar esta visita.")

    def perform_destroy(self, instance):
        if instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir esta visita.")
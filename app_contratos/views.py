# C:\wamp64\www\ImobCloud\app_contratos\views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Contrato
from .serializers import ContratoSerializer
from django.shortcuts import get_object_or_404

class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all() # Necessário para o router
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.tenant:
            return Contrato.objects.filter(imobiliaria=self.request.tenant)
        return Contrato.objects.none()

    def perform_create(self, serializer):
        # Garante que o imóvel e cliente associados pertencem ao tenant atual
        imovel_id = self.request.data.get('imovel')
        cliente_id = self.request.data.get('cliente')

        from app_imoveis.models import Imovel
        from app_clientes.models import Cliente
        
        imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)
        cliente = get_object_or_404(Cliente, pk=cliente_id, imobiliaria=self.request.tenant)

        if self.request.tenant:
            serializer.save(imobiliaria=self.request.tenant, imovel=imovel, cliente=cliente)
        else:
            raise Exception("Não foi possível associar o contrato a uma imobiliária. Tenant não identificado.")

    def perform_update(self, serializer):
        if serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este contrato.")

    def perform_destroy(self, instance):
        if instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir este contrato.")
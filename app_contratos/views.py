# C:\wamp64\www\ImobCloud\app_contratos\views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Contrato
from .serializers import ContratoSerializer
from django.shortcuts import get_object_or_404
# Import Imovel e Cliente para ContratoViewSet
from app_imoveis.models import Imovel 
from app_clientes.models import Cliente

class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # NOVO: Se o usuário é superusuário, ele vê TODOS os contratos
        if self.request.user.is_superuser:
            return Contrato.objects.all()
        # Se não é superusuário, filtra pela imobiliária associada ao request
        elif self.request.tenant:
            return Contrato.objects.filter(imobiliaria=self.request.tenant)
        return Contrato.objects.none()

    def perform_create(self, serializer):
        imovel_id = self.request.data.get('imovel')
        cliente_id = self.request.data.get('cliente')

        # NOVO: Superusuário pode associar a qualquer imóvel/cliente.
        # Usuário normal só pode associar a imóvel/cliente da sua imobiliária.
        if self.request.user.is_superuser:
            imovel = get_object_or_404(Imovel, pk=imovel_id)
            cliente = get_object_or_404(Cliente, pk=cliente_id)
            if 'imobiliaria' in self.request.data: # Permite superuser definir imobiliaria
                imobiliaria_obj = get_object_or_404(self.request.tenant._meta.model, pk=self.request.data['imobiliaria'])
                serializer.save(imobiliaria=imobiliaria_obj, imovel=imovel, cliente=cliente)
            else: # Se superuser não definiu, usa o tenant identificado (pode ser None)
                serializer.save(imobiliaria=self.request.tenant, imovel=imovel, cliente=cliente) # Fallback para tenant
        elif self.request.tenant:
            imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)
            cliente = get_object_or_404(Cliente, pk=cliente_id, imobiliaria=self.request.tenant)
            serializer.save(imobiliaria=self.request.tenant, imovel=imovel, cliente=cliente)
        else:
            raise Exception("Não foi possível associar o contrato. Tenant não identificado ou inválido.")

    def perform_update(self, serializer):
        # NOVO: Superusuário pode atualizar qualquer contrato
        if self.request.user.is_superuser:
            serializer.save()
        # Usuário normal só pode atualizar contratos da sua imobiliária
        elif serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este contrato.")

    def perform_destroy(self, instance):
        # NOVO: Superusuário pode excluir qualquer contrato
        if self.request.user.is_superuser:
            instance.delete()
        # Usuário normal só pode excluir contratos da sua imobiliária
        elif instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir este contrato.")
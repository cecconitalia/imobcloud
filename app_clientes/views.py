# C:\wamp64\www\ImobCloud\app_clientes\views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Cliente, Visita
from .serializers import ClienteSerializer, VisitaSerializer
from django.shortcuts import get_object_or_404
# Import Imovel para VisitaViewSet
from app_imoveis.models import Imovel 

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # NOVO: Se o usuário é superusuário, ele vê TODOS os clientes
        if self.request.user.is_superuser:
            return Cliente.objects.all()
        # Se não é superusuário, filtra pela imobiliária associada ao request
        elif self.request.tenant:
            return Cliente.objects.filter(imobiliaria=self.request.tenant)
        return Cliente.objects.none()

    def perform_create(self, serializer):
        # NOVO: Superusuário pode criar para qualquer imobiliária
        if self.request.user.is_superuser and 'imobiliaria' in self.request.data:
            imobiliaria_id = self.request.data['imobiliaria']
            imobiliaria_obj = get_object_or_404(self.request.tenant._meta.model, pk=imobiliaria_id)
            serializer.save(imobiliaria=imobiliaria_obj)
        elif self.request.tenant:
            serializer.save(imobiliaria=self.request.tenant)
        else:
            raise Exception("Não foi possível associar o cliente a uma imobiliária. Tenant não identificado.")

    def perform_update(self, serializer):
        # NOVO: Superusuário pode atualizar qualquer cliente
        if self.request.user.is_superuser:
            serializer.save()
        # Usuário normal só pode atualizar clientes da sua imobiliária
        elif serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este cliente.")

    def perform_destroy(self, instance):
        # NOVO: Superusuário pode excluir qualquer cliente
        if self.request.user.is_superuser:
            instance.delete()
        # Usuário normal só pode excluir clientes da sua imobiliária
        elif instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir este cliente.")


class VisitaViewSet(viewsets.ModelViewSet):
    queryset = Visita.objects.all()
    serializer_class = VisitaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # NOVO: Se o usuário é superusuário, ele vê TODAS as visitas
        if self.request.user.is_superuser:
            return Visita.objects.all()
        # Se não é superusuário, filtra pela imobiliária associada ao request
        elif self.request.tenant:
            return Visita.objects.filter(imobiliaria=self.request.tenant)
        return Visita.objects.none()

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
                serializer.save(imobiliaria=imobiliaria_obj, cliente=cliente, imovel=imovel)
            else: # Se superuser não definiu, usa o tenant identificado (pode ser None)
                serializer.save(imobiliaria=self.request.tenant, cliente=cliente, imovel=imovel) # Fallback para tenant
        elif self.request.tenant:
            imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)
            cliente = get_object_or_404(Cliente, pk=cliente_id, imobiliaria=self.request.tenant)
            serializer.save(imobiliaria=self.request.tenant, cliente=cliente, imovel=imovel)
        else:
            raise Exception("Não foi possível associar a visita. Tenant não identificado ou inválido.")

    def perform_update(self, serializer):
        # NOVO: Superusuário pode atualizar qualquer visita
        if self.request.user.is_superuser:
            serializer.save()
        # Usuário normal só pode atualizar visitas da sua imobiliária
        elif serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar esta visita.")

    def perform_destroy(self, instance):
        # NOVO: Superusuário pode excluir qualquer visita
        if self.request.user.is_superuser:
            instance.delete()
        # Usuário normal só pode excluir visitas da sua imobiliária
        elif instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir esta visita.")
# C:\wamp64\www\ImobCloud\app_imoveis\views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated # COMENTADO/REMOVIDO TEMPORARIAMENTE
from .models import Imovel, ImagemImovel
from .serializers import ImovelSerializer, ImagemImovelSerializer
from django.shortcuts import get_object_or_404

class ImovelViewSet(viewsets.ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    # permission_classes = [IsAuthenticated] # COMENTADO/REMOVIDO TEMPORARIAMENTE

    def get_queryset(self):
        # GARANTE QUE APENAS OS IMÓVEIS DA IMOBILIÁRIA ATUAL SÃO RETORNADOS
        if self.request.tenant:
            return Imovel.objects.filter(imobiliaria=self.request.tenant)
        return Imovel.objects.none()

    def perform_create(self, serializer):
        if self.request.tenant:
            serializer.save(imobiliaria=self.request.tenant)
        else:
            raise Exception("Não foi possível associar o imóvel a uma imobiliária. Tenant não identificado ou inválido.")

    def perform_update(self, serializer):
        if serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este imóvel. Ele não pertence à sua imobiliária.")

    def perform_destroy(self, instance):
        if instance.imovel.imobiliaria == self.request.tenant: # CORREÇÃO: era instance.imobiliaria
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir este imóvel. Ele não pertence à sua imobiliária.")


class ImagemImovelViewSet(viewsets.ModelViewSet):
    queryset = ImagemImovel.objects.all()
    serializer_class = ImagemImovelSerializer
    # permission_classes = [IsAuthenticated] # COMENTADO/REMOVIDO TEMPORARIAMENTE

    def get_queryset(self):
        if self.request.tenant:
            return ImagemImovel.objects.filter(imovel__imobiliaria=self.request.tenant)
        return ImagemImovel.objects.none()

    def perform_create(self, serializer):
        imovel_id = self.request.data.get('imovel')
        try:
            from app_imoveis.models import Imovel # Importação local para evitar dependência circular se ocorrer
            imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)
            serializer.save(imovel=imovel)
        except Imovel.DoesNotExist:
            raise Exception("Imóvel não encontrado ou não pertence à sua imobiliária.")

    def perform_update(self, serializer):
        if serializer.instance.imovel.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar esta imagem. O imóvel associado não pertence à sua imobiliária.")

    def perform_destroy(self, instance):
        if instance.imovel.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir esta imagem. O imóvel associado não pertence à sua imobiliária.")
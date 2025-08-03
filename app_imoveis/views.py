# C:\wamp64\www\ImobCloud\app_imoveis\views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions 
from django.shortcuts import get_object_or_404
from .models import Imovel, ImagemImovel
from .serializers import ImovelSerializer, ImagemImovelSerializer
from core.models import Imobiliaria 

class ImovelViewSet(viewsets.ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    # PARA DIAGNÓSTICO: Permite acesso TOTAL para QUALQUER UM
    permission_classes = [permissions.AllowAny] 

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Imovel.objects.all()
        elif self.request.tenant:
            return Imovel.objects.filter(imobiliaria=self.request.tenant)
        
        subdomain_param = self.request.query_params.get('subdomain', None)
        if subdomain_param:
            try:
                imobiliaria_por_param = Imobiliaria.objects.get(subdomino=subdomain_param)
                return Imovel.objects.filter(imobiliaria=imobiliaria_por_param)
            except Imobiliaria.DoesNotExist:
                return Imovel.objects.none()

        return Imovel.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_superuser and 'imobiliaria' in self.request.data:
            imobiliaria_id = self.request.data['imobiliaria']
            imobiliaria_obj = get_object_or_404(Imobiliaria, pk=imobiliaria_id)
            serializer.save(imobiliaria=imobiliaria_obj)
        elif self.request.tenant:
            serializer.save(imobiliaria=self.request.tenant)
        else:
            raise Exception("Não foi possível associar o imóvel a uma imobiliária. Tenant não identificado ou inválido.")

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este imóvel. Ele não pertence à sua imobiliária.")

    def perform_destroy(self, instance):
        # Esta lógica está correta, mas o problema pode estar na permissão antes dela ser chamada
        if self.request.user.is_superuser:
            instance.delete()
        elif instance.imobiliaria == self.request.tenant:
            instance.delete()
        else:
            raise Exception("Você não tem permissão para excluir este imóvel. Ele não pertence à sua imobiliária.")

class ImagemImovelViewSet(viewsets.ModelViewSet):
    queryset = ImagemImovel.objects.all() 
    serializer_class = ImagemImovelSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ImagemImovel.objects.all()
        elif self.request.tenant:
            return ImagemImovel.objects.filter(imovel__imobiliaria=self.request.tenant)
        
        subdomain_param = self.request.query_params.get('subdomain', None)
        if subdomain_param:
            try:
                imobiliaria_por_param = Imobiliaria.objects.get(subdomino=subdomain_param)
                return ImagemImovel.objects.filter(imovel__imobiliaria=imobiliaria_por_param)
            except Imobiliaria.DoesNotExist:
                return ImagemImovel.objects.none()

        return ImagemImovel.objects.none()

    def perform_create(self, serializer):
        imovel_id = self.request.data.get('imovel')
        if self.request.user.is_superuser:
            imovel = get_object_or_404(Imovel, pk=imovel_id)
        elif self.request.tenant:
            imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)
        else:
            raise Exception("Imóvel não encontrado ou não pertence à sua imobiliária.")
            
        if self.request.data.get('principal', False): 
             ImagemImovel.objects.filter(imovel=imovel, principal=True).update(principal=False)
        elif not ImagemImovel.objects.filter(imovel=imovel, principal=True).exists():
             serializer.validated_data['principal'] = True

        serializer.save(imovel=imovel)

    def perform_update(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        elif serializer.instance.imovel.imobiliaria == self.request.tenant:
            if serializer.validated_data.get('principal', False): 
                ImagemImovel.objects.filter(imovel=serializer.instance.imovel, principal=True).update(principal=False)
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar esta imagem. O imóvel associado não pertence à sua imobiliária.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser:
            instance.delete()
            if instance.principal:
                remaining_images = ImagemImovel.objects.filter(imovel=instance.imovel).order_by('data_upload').first()
                if remaining_images:
                    remaining_images.principal = True
                    remaining_images.save()
        elif instance.imovel.imobiliaria == self.request.tenant:
            instance.delete()
            if instance.principal:
                remaining_images = ImagemImovel.objects.filter(imovel=instance.imovel).order_by('data_upload').first()
                if remaining_images:
                    remaining_images.principal = True
                    remaining_images.save()
        else:
            raise Exception("Você não tem permissão para excluir esta imagem. O imóvel associado não pertence à sua imobiliária.")
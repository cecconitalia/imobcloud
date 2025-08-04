# C:\wamp64\www\ImobCloud\app_imoveis\views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions 
from django.shortcuts import get_object_or_404
from rest_framework import filters

from .models import Imovel, ImagemImovel
from .serializers import ImovelSerializer, ImagemImovelSerializer
from core.models import Imobiliaria 

class ImovelViewSet(viewsets.ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['endereco', 'cidade', 'descricao']

    def get_queryset(self):
        base_queryset = Imovel.objects.exclude(status='Desativado')

        # Lógica para utilizadores autenticados (painel) continua a funcionar como antes
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                return base_queryset.all()
            elif self.request.tenant:
                return base_queryset.filter(imobiliaria=self.request.tenant)

        # Lógica para o site público (utilizadores anónimos)
        # O middleware identifica o tenant pelo HOST (ex: sol.localhost)
        if self.request.tenant:
            return base_queryset.filter(imobiliaria=self.request.tenant)
        
        # Fallback para o site público, que irá enviar um parâmetro de URL
        subdomain_param = self.request.query_params.get('subdomain', None)
        if subdomain_param:
            try:
                # --- LINHA CORRIGIDA ---
                # Corrigido de 'subdomino' para 'subdominio' para corresponder ao modelo
                imobiliaria_por_param = Imobiliaria.objects.get(subdominio=subdomain_param)
                return base_queryset.filter(imobiliaria=imobiliaria_por_param)
            except Imobiliaria.DoesNotExist:
                return Imovel.objects.none()

        # Se nenhum tenant for identificado, retorna uma lista vazia
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
        if self.request.user.is_superuser or instance.imobiliaria == self.request.tenant:
            instance.status = 'Desativado'
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise Exception("Você não tem permissão para inativar este imóvel. Ele não pertence à sua imobiliária.")


class ImagemImovelViewSet(viewsets.ModelViewSet):
    # Nenhuma alteração neste ViewSet
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
                imobiliaria_por_param = Imobiliaria.objects.get(subdominio=subdomain_param)
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
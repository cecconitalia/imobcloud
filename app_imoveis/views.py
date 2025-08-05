# C:\wamp64\www\ImobCloud\app_imoveis\views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from rest_framework import filters
from django.core.mail import send_mail
from rest_framework.decorators import action

from .models import Imovel, ImagemImovel, ContatoImovel
from .serializers import ImovelSerializer, ImagemImovelSerializer, ContatoImovelSerializer
from core.models import Imobiliaria, PerfilUsuario

class ImovelViewSet(viewsets.ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # O SearchFilter continua útil para a pesquisa geral no painel de admin
    filter_backends = [filters.SearchFilter]
    search_fields = ['endereco', 'cidade', 'descricao']

    def get_queryset(self):
        base_queryset = Imovel.objects.exclude(status='Desativado')

        # --- LÓGICA DE FILTRO ATUALIZADA ---

        # 1. Filtros para o site público (vindos como query params)
        finalidade = self.request.query_params.get('finalidade', None)
        tipo = self.request.query_params.get('tipo', None)
        cidade = self.request.query_params.get('cidade', None)

        if finalidade:
            base_queryset = base_queryset.filter(finalidade=finalidade)
        if tipo:
            base_queryset = base_queryset.filter(tipo=tipo)
        if cidade:
            # Usamos __icontains para uma pesquisa de texto flexível (case-insensitive)
            base_queryset = base_queryset.filter(cidade__icontains=cidade)

        # 2. Lógica de tenant (multi-imobiliária)
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                return base_queryset.all()
            elif self.request.tenant:
                return base_queryset.filter(imobiliaria=self.request.tenant)

        subdomain_param = self.request.query_params.get('subdomain', None)
        if subdomain_param:
            try:
                imobiliaria_por_param = Imobiliaria.objects.get(subdominio=subdomain_param)
                return base_queryset.filter(imobiliaria=imobiliaria_por_param)
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
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo in [PerfilUsuario.Cargo.ADMIN, PerfilUsuario.Cargo.CORRETOR] and serializer.instance.imobiliaria == self.request.tenant:
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar este imóvel. Ele não pertence à sua imobiliária.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and instance.imobiliaria == self.request.tenant):
            instance.status = 'Desativado'
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise Exception("Você não tem permissão para inativar este imóvel. Ele não pertence à sua imobiliária.")


# ... O restante do ficheiro (ContatoImovelViewSet, ImagemImovelViewSet) permanece igual ...
class ContatoImovelViewSet(viewsets.ModelViewSet):
    """
    Endpoint para receber mensagens de contato do site público.
    Permite a criação (envio do formulário) sem autenticação,
    mas restringe as demais operações a utilizadores autenticados.
    """
    # ATUALIZADO
    queryset = ContatoImovel.objects.all()
    serializer_class = ContatoImovelSerializer
    
    def get_permissions(self):
        # Permite POST (criação) para todos, mas exige autenticação para outras operações.
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def get_queryset(self):
        # ATUALIZADO
        base_queryset = ContatoImovel.objects.filter(arquivado=False)
        if self.request.user.is_superuser:
            return base_queryset.all()
        elif self.request.user.is_authenticated and self.request.tenant:
            # ATUALIZADO
            return base_queryset.filter(imovel__imobiliaria=self.request.tenant)
        return ContatoImovel.objects.none()

    def perform_create(self, serializer):
        # Guardamos o objeto de contacto primeiro para ter acesso a ele
        contato = serializer.save()

        # Lógica de envio de email
        try:
            imobiliaria = contato.imovel.imobiliaria
            
            # Verifica se a imobiliária tem um email de contato configurado
            if hasattr(imobiliaria, 'email_contato') and imobiliaria.email_contato:
                destinatario_email = imobiliaria.email_contato

                assunto = f"Novo Contato para o Imóvel: {contato.imovel.endereco}"
                mensagem_corpo = f"""
                Você recebeu um novo contato através do site!

                Imóvel: {contato.imovel.endereco} (ID: {contato.imovel.id})
                Nome do Interessado: {contato.nome}
                Email: {contato.email}
                Telefone: {contato.telefone or 'Não informado'}

                Mensagem:
                {contato.mensagem}
                """
                remetente = 'nao-responda@imobcloud.com' # Remetente genérico

                send_mail(
                    assunto,
                    mensagem_corpo,
                    remetente,
                    [destinatario_email], # O destinatário deve estar numa lista
                    fail_silently=False,
                )
                print(f"DEBUG: Email de notificação preparado para {destinatario_email}.")
            else:
                print(f"AVISO: Imobiliária '{imobiliaria.nome}' não possui email de contato configurado. Email não enviado.")

        except Exception as e:
            # Se o email falhar, não quebramos a aplicação, apenas registamos o erro
            print(f"ERRO AO ENVIAR EMAIL DE NOTIFICAÇÃO: {e}")

    # NOVO: Ação para arquivar um contacto
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def arquivar(self, request, pk=None):
        """
        Marca um contacto como arquivado.
        """
        contato = self.get_object()
        # Verifica a permissão (só superuser ou admin da imobiliária do contacto)
        is_superuser = request.user.is_superuser
        is_admin_of_tenant = (
            hasattr(request.user, 'perfil') and
            request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and
            contato.imovel.imobiliaria == request.tenant
        )

        if not (is_superuser or is_admin_of_tenant):
            return Response(
                {"detail": "Você não tem permissão para arquivar este contacto."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        contato.arquivado = True
        contato.save()
        return Response({'status': 'Contacto arquivado com sucesso'}, status=status.HTTP_200_OK)


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
                imobiliaria_por_param = Imobiliaria.objects.get(subdominio=subdomain_param)
                return ImagemImovel.objects.filter(imovel__imobiliaria=imobiliaria_por_param)
            except Imobiliaria.DoesNotExist:
                return ImagemImovel.objects.none()

        return ImagemImovel.objects.none()

    def perform_create(self, serializer):
        imovel_id = self.request.data.get('imovel')
        # Apenas ADMINs e superusuários podem criar imagens. Corretores não podem.
        if self.request.user.is_superuser:
            imovel = get_object_or_404(Imovel, pk=imovel_id)
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and self.request.tenant:
            imovel = get_object_or_404(Imovel, pk=imovel_id, imobiliaria=self.request.tenant)
        else:
            raise Exception("Você não tem permissão para adicionar imagens.")
            
        if self.request.data.get('principal', False):
             ImagemImovel.objects.filter(imovel=imovel, principal=True).update(principal=False)
        elif not ImagemImovel.objects.filter(imovel=imovel, principal=True).exists():
             serializer.validated_data['principal'] = True

        serializer.save(imovel=imovel)

    def perform_update(self, serializer):
        # Apenas ADMINs e superusuários podem atualizar imagens.
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and serializer.instance.imovel.imobiliaria == self.request.tenant:
            if serializer.validated_data.get('principal', False):
                ImagemImovel.objects.filter(imovel=serializer.instance.imovel, principal=True).update(principal=False)
            serializer.save()
        else:
            raise Exception("Você não tem permissão para atualizar esta imagem. O imóvel associado não pertence à sua imobiliária.")

    def perform_destroy(self, instance):
        # Apenas ADMINs e superusuários podem excluir imagens.
        if self.request.user.is_superuser:
            instance.delete()
            if instance.principal:
                remaining_images = ImagemImovel.objects.filter(imovel=instance.imovel).order_by('data_upload').first()
                if remaining_images:
                    remaining_images.principal = True
                    remaining_images.save()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and instance.imovel.imobiliaria == self.request.tenant:
            instance.delete()
            if instance.principal:
                remaining_images = ImagemImovel.objects.filter(imovel=instance.imovel).order_by('data_upload').first()
                if remaining_images:
                    remaining_images.principal = True
                    remaining_images.save()
        else:
            raise Exception("Você não tem permissão para excluir esta imagem. O imóvel associado não pertence à sua imobiliária.")
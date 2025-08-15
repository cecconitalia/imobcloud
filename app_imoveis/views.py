from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework import filters
from django.core.mail import send_mail
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.db import models, transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Count, Q, Case, When, Value, CharField, Max
from io import BytesIO
from xhtml2pdf import pisa
import locale
from num2words import num2words
from datetime import date, timedelta
from decimal import Decimal

from .models import Imovel, ImagemImovel, ContatoImovel
from .serializers import ImovelSerializer, ImagemImovelSerializer, ContatoImovelSerializer, ImovelPublicSerializer
from core.models import Imobiliaria, PerfilUsuario
from app_clientes.models import Oportunidade

# ===================================================================
# VIEWS PÚBLICAS (Para o site de cada imobiliária, sem necessidade de login)
# ===================================================================

class ImovelPublicListView(ListAPIView):
    """
    View para listar os imóveis ativos de uma imobiliária (tenant) no site público.
    """
    serializer_class = ImovelPublicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Imovel.objects.filter(
            imobiliaria=self.request.tenant,
            publicado_no_site=True
        ).exclude(status='DESATIVADO').order_by('-data_atualizacao')


class ImovelPublicDetailView(RetrieveAPIView):
    """
    View para detalhar um imóvel específico no site público.
    """
    serializer_class = ImovelPublicSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Imovel.objects.filter(publicado_no_site=True)
    lookup_field = 'pk'

    def get_queryset(self):
        return self.queryset.filter(imobiliaria=self.request.tenant)

# ===================================================================
# VIEWS INTERNAS (Para o painel administrativo, requerem login)
# ===================================================================

class ImovelViewSet(viewsets.ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['endereco', 'cidade', 'titulo_anuncio', 'codigo_referencia']

    def get_queryset(self):
        base_queryset = Imovel.objects.all()
        # Sua lógica de filtragem complexa é mantida intacta
        finalidade = self.request.query_params.get('finalidade', None)
        tipo = self.request.query_params.get('tipo', None)
        cidade = self.request.query_params.get('cidade', None)
        valor_min = self.request.query_params.get('valor_min', None)
        valor_max = self.request.query_params.get('valor_max', None)
        quartos_min = self.request.query_params.get('quartos_min', None)
        vagas_min = self.request.query_params.get('vagas_min', None)
        status_param = self.request.query_params.get('status', None)

        if self.action == 'list':
            if not status_param:
                base_queryset = base_queryset.exclude(status='DESATIVADO')
            else:
                base_queryset = base_queryset.filter(status=status_param)
        
        if not self.request.user.is_authenticated or not self.request.tenant:
            base_queryset = base_queryset.filter(publicado_no_site=True)

        if finalidade: base_queryset = base_queryset.filter(finalidade=finalidade)
        if tipo: base_queryset = base_queryset.filter(tipo=tipo)
        if cidade: base_queryset = base_queryset.filter(cidade__icontains=cidade)
        if valor_min: base_queryset = base_queryset.filter(valor_venda__gte=valor_min)
        if valor_max: base_queryset = base_queryset.filter(valor_venda__lte=valor_max)
        if quartos_min: base_queryset = base_queryset.filter(quartos__gte=quartos_min)
        if vagas_min: base_queryset = base_queryset.filter(vagas_garagem__gte=vagas_min)
        
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
            raise PermissionDenied("Não foi possível associar o imóvel a uma imobiliária.")

    def perform_update(self, serializer):
        if self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and serializer.instance.imobiliaria == self.request.tenant):
            serializer.save()
        else:
            raise PermissionDenied("Você não tem permissão para atualizar este imóvel.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and instance.imobiliaria == self.request.tenant):
            instance.status = 'DESATIVADO'
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise PermissionDenied("Você não tem permissão para inativar este imóvel.")


class ImagemImovelViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Imagens de Imóveis. O uso de ModelViewSet garante
    que todos os métodos HTTP (GET, POST, PUT, DELETE) estejam habilitados por padrão.
    """
    queryset = ImagemImovel.objects.all()
    serializer_class = ImagemImovelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ImagemImovel.objects.all()
        if self.request.tenant:
            return ImagemImovel.objects.filter(imovel__imobiliaria=self.request.tenant)
        return ImagemImovel.objects.none()

    def perform_create(self, serializer):
        """
        Lógica para criar uma nova imagem, associando-a a um imóvel
        e definindo sua ordem e se é a imagem principal.
        """
        imovel_id = self.request.data.get('imovel')
        imovel = get_object_or_404(Imovel, pk=imovel_id)

        if not (self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and imovel.imobiliaria == self.request.tenant)):
            raise PermissionDenied("Você não tem permissão para adicionar imagens a este imóvel.")

        e_primeira_imagem = not ImagemImovel.objects.filter(imovel=imovel).exists()
        
        max_ordem_result = ImagemImovel.objects.filter(imovel=imovel).aggregate(Max('ordem'))
        max_ordem = max_ordem_result['ordem__max'] if max_ordem_result['ordem__max'] is not None else -1
        nova_ordem = max_ordem + 1

        serializer.save(imovel=imovel, ordem=nova_ordem, principal=e_primeira_imagem)

    def perform_destroy(self, instance):
        """
        Lógica para deletar uma imagem, garantindo que se a imagem
        principal for removida, a próxima da ordem se torne a principal.
        """
        if not (self.request.user.is_superuser or (hasattr(self.request.user, 'perfil') and instance.imovel.imobiliaria == self.request.tenant)):
            raise PermissionDenied("Você não tem permissão para excluir esta imagem.")
        
        imovel_da_imagem = instance.imovel
        era_principal = instance.principal
        instance.delete()

        if era_principal and ImagemImovel.objects.filter(imovel=imovel_da_imagem).exists():
            proxima_imagem = ImagemImovel.objects.filter(imovel=imovel_da_imagem).order_by('ordem').first()
            if proxima_imagem:
                proxima_imagem.principal = True
                proxima_imagem.save()
    
    @action(detail=False, methods=['post'], url_path='reordenar')
    @transaction.atomic
    def reordenar_imagens(self, request, *args, **kwargs):
        """
        Ação customizada para reordenar uma lista de imagens de uma só vez.
        """
        ordem_ids = request.data.get('ordem_ids', [])
        if not ordem_ids:
            return Response({'detail': 'A lista de IDs de imagem é necessária.'}, status=status.HTTP_400_BAD_REQUEST)

        imagens = ImagemImovel.objects.filter(id__in=ordem_ids)
        if not request.user.is_superuser:
            imagens = imagens.filter(imovel__imobiliaria=request.tenant)
        
        if len(ordem_ids) != imagens.count():
            raise PermissionDenied("Uma ou mais imagens não foram encontradas ou não pertencem à sua imobiliária.")

        for index, image_id in enumerate(ordem_ids):
            ImagemImovel.objects.filter(id=image_id).update(ordem=index, principal=(index == 0))
            
        return Response({'status': 'Ordem das imagens atualizada com sucesso.'}, status=status.HTTP_200_OK)


class ContatoImovelViewSet(viewsets.ModelViewSet):
    # Sua lógica para ContatoImovelViewSet mantida intacta
    queryset = ContatoImovel.objects.all()
    serializer_class = ContatoImovelSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def get_queryset(self):
        base_queryset = ContatoImovel.objects.filter(arquivado=False)
        if self.request.user.is_superuser:
            return base_queryset.all()
        elif self.request.user.is_authenticated and self.request.tenant:
            return base_queryset.filter(imovel__imobiliaria=self.request.tenant)
        return ContatoImovel.objects.none()

    def perform_create(self, serializer):
        contato = serializer.save()
        try:
            imobiliaria = contato.imovel.imobiliaria
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
                remetente = 'nao-responda@imobcloud.com'
                send_mail(assunto, mensagem_corpo, remetente, [destinatario_email], fail_silently=False)

            oportunidade_associada = Oportunidade.objects.filter(imovel=contato.imovel).first()
            if oportunidade_associada and oportunidade_associada.responsavel:
                destinatario_notificacao = oportunidade_associada.responsavel
                Notificacao.objects.create(
                    destinatario=destinatario_notificacao,
                    mensagem=f"Novo contato de '{contato.nome}' para o imóvel '{contato.imovel.endereco}'.",
                    link=f"/contatos"
                )
        except Exception as e:
            print(f"ERRO AO ENVIAR NOTIFICAÇÕES: {e}")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def arquivar(self, request, pk=None):
        contato = self.get_object()
        if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and contato.imovel.imobiliaria == request.tenant)):
            raise PermissionDenied("Você não tem permissão para arquivar este contacto.")
        
        contato.arquivado = True
        contato.save()
        return Response({'status': 'Contacto arquivado com sucesso'}, status=status.HTTP_200_OK)


class GerarAutorizacaoPDFView(APIView):
    # Sua lógica para gerar PDF mantida intacta
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, imovel_id, *args, **kwargs):
        imovel = get_object_or_404(Imovel, pk=imovel_id)
        if not request.user.is_superuser and imovel.imobiliaria != request.tenant:
            return HttpResponse("Acesso negado.", status=403)
        if not imovel.proprietario:
            return HttpResponse("Erro: O imóvel não possui um proprietário vinculado.", status=400)
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except locale.Error:
            locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        hoje = date.today()
        finalidade_texto = "venda" if imovel.status == 'A_VENDA' else "locação"
        valor = imovel.valor_venda if imovel.status == 'A_VENDA' else imovel.valor_aluguel
        valor = valor or Decimal(0)
        reais = int(valor)
        centavos = int((valor - reais) * 100)
        valor_por_extenso = num2words(reais, lang='pt_BR') + " reais"
        if centavos > 0:
            valor_por_extenso += " e " + num2words(centavos, lang='pt_BR') + " centavos"
        context = {
            'imovel': imovel,
            'proprietario': imovel.proprietario,
            'imobiliaria': imovel.imobiliaria,
            'finalidade_texto': finalidade_texto,
            'valor': valor,
            'valor_por_extenso': valor_por_extenso,
            'comissao_por_extenso': num2words(imovel.comissao_percentual or 0, lang='pt_BR') + " por cento",
            'data_hoje': hoje,
            'mes_hoje': hoje.strftime("%B")
        }
        html_string = render_to_string('autorizacao_template.html', context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="autorizacao_imovel_{imovel.codigo_referencia}.pdf"'
            return response
        return HttpResponse(f"Erro ao gerar o PDF: {pdf.err}", status=500)


class AutorizacaoStatusView(APIView):
    # Sua lógica para o status de autorização mantida intacta
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN)):
            return Response({"detail": "Acesso não autorizado."}, status=status.HTTP_403_FORBIDDEN)
        tenant = request.tenant
        if not tenant and request.user.is_superuser:
            tenant = Imobiliaria.objects.first()
        if not tenant:
            return Response({"error": "Nenhuma imobiliária associada."}, status=status.HTTP_400_BAD_REQUEST)
        hoje = timezone.now().date()
        limite_30_dias = hoje + timedelta(days=30)
        limite_passado_30_dias = hoje - timedelta(days=30)
        base_queryset = Imovel.objects.filter(imobiliaria=tenant).exclude(status='DESATIVADO')
        sumario = base_queryset.aggregate(
            expirando_em_30_dias=Count('id', filter=Q(data_fim_autorizacao__gte=hoje, data_fim_autorizacao__lte=limite_30_dias)),
            expiradas_recentemente=Count('id', filter=Q(data_fim_autorizacao__lt=hoje, data_fim_autorizacao__gte=limite_passado_30_dias)),
            ativas=Count('id', filter=Q(data_fim_autorizacao__gte=hoje)),
            sem_data=Count('id', filter=Q(data_fim_autorizacao__isnull=True)),
        )
        imoveis_com_status = base_queryset.annotate(
            status_autorizacao=Case(
                When(data_fim_autorizacao__isnull=True, then=Value('Incompleto')),
                When(data_fim_autorizacao__lt=hoje, then=Value('Expirado')),
                When(data_fim_autorizacao__lte=limite_30_dias, then=Value('Expirando')),
                default=Value('Ativo'),
                output_field=CharField(),
            )
        ).values(
            'id', 'codigo_referencia', 'titulo_anuncio', 'proprietario__nome_completo',
            'data_captacao', 'data_fim_autorizacao', 'status_autorizacao'
        )
        data = {
            'sumario': sumario,
            'imoveis': list(imoveis_com_status)
        }
        return Response(data)
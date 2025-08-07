# C:\wamp64\www\ImobCloud\app_imoveis\views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from rest_framework import filters
from django.core.mail import send_mail
from rest_framework.decorators import action

from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.views import APIView
from io import BytesIO
from xhtml2pdf import pisa
import locale
from num2words import num2words
from datetime import date, timedelta
from decimal import Decimal

# IMPORTAÇÕES PARA A VIEW DE STATUS
from django.utils import timezone
from django.db.models import Count, Q, Case, When, Value, CharField

from .models import Imovel, ImagemImovel, ContatoImovel
from .serializers import ImovelSerializer, ImagemImovelSerializer, ContatoImovelSerializer
from core.models import Imobiliaria, PerfilUsuario, Notificacao
from app_clientes.models import Oportunidade

class ImovelViewSet(viewsets.ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['endereco', 'cidade', 'titulo_anuncio', 'codigo_referencia']

    def get_queryset(self):
        base_queryset = Imovel.objects.exclude(status='DESATIVADO')

        # Filtro para o site público
        if not self.request.user.is_authenticated or not self.request.tenant:
            base_queryset = base_queryset.filter(publicado_no_site=True)

        finalidade = self.request.query_params.get('finalidade', None)
        tipo = self.request.query_params.get('tipo', None)
        cidade = self.request.query_params.get('cidade', None)
        valor_min = self.request.query_params.get('valor_min', None)
        valor_max = self.request.query_params.get('valor_max', None)
        quartos_min = self.request.query_params.get('quartos_min', None)
        vagas_min = self.request.query_params.get('vagas_min', None)

        if finalidade:
            base_queryset = base_queryset.filter(finalidade=finalidade)
        if tipo:
            base_queryset = base_queryset.filter(tipo=tipo)
        if cidade:
            base_queryset = base_queryset.filter(cidade__icontains=cidade)
        if valor_min:
            base_queryset = base_queryset.filter(valor_venda__gte=valor_min)
        if valor_max:
            base_queryset = base_queryset.filter(valor_venda__lte=valor_max)
        if quartos_min:
            base_queryset = base_queryset.filter(quartos__gte=quartos_min)
        if vagas_min:
            base_queryset = base_queryset.filter(vagas_garagem__gte=vagas_min)

        # Lógica de Tenant (Multi-imobiliária)
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
            instance.status = 'DESATIVADO'
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise Exception("Você não tem permissão para inativar este imóvel. Ele não pertence à sua imobiliária.")


class ContatoImovelViewSet(viewsets.ModelViewSet):
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
        is_superuser = request.user.is_superuser
        is_admin_of_tenant = (
            hasattr(request.user, 'perfil') and
            request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and
            contato.imovel.imobiliaria == self.request.tenant
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
        if self.request.user.is_superuser:
            serializer.save()
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and serializer.instance.imovel.imobiliaria == self.request.tenant:
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
        elif hasattr(self.request.user, 'perfil') and self.request.user.perfil.cargo == PerfilUsuario.Cargo.ADMIN and instance.imovel.imobiliaria == self.request.tenant:
            instance.delete()
            if instance.principal:
                remaining_images = ImagemImovel.objects.filter(imovel=instance.imovel).order_by('data_upload').first()
                if remaining_images:
                    remaining_images.principal = True
                    remaining_images.save()
        else:
            raise Exception("Você não tem permissão para excluir esta imagem. O imóvel associado não pertence à sua imobiliária.")


class GerarAutorizacaoPDFView(APIView):
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
            'proprietario_endereco': "[Endereço do Proprietário]",
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
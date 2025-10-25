# C:\wamp64\www\ImobCloud\app_imoveis\views.py

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
from django.http import HttpResponse, QueryDict
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Count, Q, Case, When, Value, CharField, Max
from io import BytesIO
from xhtml2pdf import pisa
import locale
from num2words import num2words
from datetime import date, timedelta
from decimal import Decimal
import json
import requests
import google.generativeai as genai
import os
from django.conf import settings
from django.db.models.fields import DecimalField, IntegerField, CharField, BooleanField

# Importamos os módulos necessários para criar a requisição de forma correta
from rest_framework.request import Request as DRFRequest
from django.test import RequestFactory


from .models import Imovel, ImagemImovel, ContatoImovel
from .serializers import ImovelSerializer, ImovelPublicSerializer, ContatoImovelSerializer, ImagemImovelSerializer
from core.models import Imobiliaria, PerfilUsuario, Notificacao
from app_clientes.models import Oportunidade
from app_config_ia.models import ModeloDePrompt
from core.serializers import ImobiliariaPublicSerializer


# Configura a API do Google Gemini
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Erro ao configurar a API do Google: {e}")


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
        
        # Filtros adicionais para busca com IA
        aceita_pet = self.request.query_params.get('aceita_pet', None)
        mobiliado = self.request.query_params.get('mobiliado', None)
        piscina = self.request.query_params.get('piscina', None)

        if not status_param:
            base_queryset = base_queryset.exclude(status='DESATIVADO')
        else:
            base_queryset = base_queryset.filter(status=status_param)
        
        if not self.request.user.is_authenticated or not self.request.tenant:
            base_queryset = base_queryset.filter(publicado_no_site=True)

        if finalidade: base_queryset = base_queryset.filter(finalidade=finalidade)
        if tipo: base_queryset = base_queryset.filter(tipo=tipo)
        if cidade: base_queryset = base_queryset.filter(cidade__icontains=cidade)
        if valor_min:
            # Filtra tanto por valor de venda quanto de aluguel se for relevante
            q_filter = Q(valor_venda__gte=valor_min) if finalidade == Imovel.Status.A_VENDA else Q(valor_aluguel__gte=valor_min)
            base_queryset = base_queryset.filter(q_filter)
        if valor_max:
            q_filter = Q(valor_venda__lte=valor_max) if finalidade == Imovel.Status.A_VENDA else Q(valor_aluguel__lte=valor_max)
            base_queryset = base_queryset.filter(q_filter)
        if quartos_min: base_queryset = base_queryset.filter(quartos__gte=quartos_min)
        if vagas_min: base_queryset = base_queryset.filter(vagas_garagem__gte=vagas_min)
        if aceita_pet: base_queryset = base_queryset.filter(aceita_pet=True)
        if mobiliado: base_queryset = base_queryset.filter(mobiliado=True)
        if piscina: base_queryset = base_queryset.filter(Q(piscina_privativa=True) | Q(piscina_condominio=True))

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


# --- NOVO ENDPOINT DE BUSCA COM IA ---
class ImovelIAView(APIView):
    """
    Endpoint de busca pública que utiliza IA para interpretar o texto do utilizador.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        user_query = request.data.get('query')
        if not user_query:
            return Response({"error": "O campo 'query' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Obter o prompt da base de dados
        try:
            prompt_config = ModeloDePrompt.objects.get(em_uso_busca=True)
            template_prompt = prompt_config.template_do_prompt
        except ModeloDePrompt.DoesNotExist:
            return Response(
                {"error": "Nenhum modelo de prompt para busca por IA está ativo. Fale com o administrador do sistema."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        prompt_final = template_prompt.replace('{{user_query}}', user_query)

        # 2. Enviar para a API da IA para traduzir o texto em JSON
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt_final)
            
            # Limpa o texto da resposta para garantir que é um JSON válido
            json_text = response.text.strip().lstrip('`json').rstrip('`').strip()
            search_params = json.loads(json_text)
            
            # IMPRIMIR O RESULTADO DA IA PARA DEBUG
            print(f"DEBUG DA IA: Parâmetros gerados para a busca: {search_params}")

        except Exception as e:
            print(f"DEBUG: Erro na API do Google Gemini durante a busca: {e}")
            return Response(
                {"error": f"Não consegui interpretar a sua pesquisa. Tente ser mais específico. ({e})"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 3. Usar os parâmetros da IA para filtrar os imóveis
        imobiliaria = request.tenant
        if not imobiliaria:
            return Response({"error": "Imobiliária não identificada."}, status=status.HTTP_400_BAD_REQUEST)
        
        # --- CÓDIGO CORRIGIDO AQUI ---
        # Refatoramos a lógica para filtrar diretamente o queryset, sem modificar o request.
        
        # Começa com o queryset base, filtrando pelo tenant
        base_queryset = Imovel.objects.filter(
            imobiliaria=imobiliaria,
            publicado_no_site=True
        ).exclude(status=Imovel.Status.DESATIVADO)
        
        # Aplica os filtros extraídos da IA
        if 'finalidade' in search_params:
            finalidade_param = search_params['finalidade']
            if finalidade_param in Imovel.Finalidade.values:
                base_queryset = base_queryset.filter(finalidade=finalidade_param)

        if 'tipo' in search_params:
            tipo_param = search_params['tipo'].upper()
            if tipo_param in Imovel.TipoImovel.names:
                base_queryset = base_queryset.filter(tipo=tipo_param)
        
        if 'cidade' in search_params:
            base_queryset = base_queryset.filter(cidade__icontains=search_params['cidade'])
        
        # Filtros de valor, quartos e vagas
        if 'valor_min' in search_params:
            base_queryset = base_queryset.filter(valor_venda__gte=search_params['valor_min'])
        if 'valor_max' in search_params:
            base_queryset = base_queryset.filter(valor_venda__lte=search_params['valor_max'])

        if 'quartos_min' in search_params:
            base_queryset = base_queryset.filter(quartos__gte=search_params['quartos_min'])
        if 'vagas_min' in search_params:
            base_queryset = base_queryset.filter(vagas_garagem__gte=search_params['vagas_min'])
            
        # Filtros booleanos
        if search_params.get('aceita_pet') == True:
            base_queryset = base_queryset.filter(aceita_pet=True)
        if search_params.get('mobiliado') == True:
            base_queryset = base_queryset.filter(mobiliado=True)
        if search_params.get('piscina') == True:
            base_queryset = base_queryset.filter(Q(piscina_privativa=True) | Q(piscina_condominio=True))
            
        serializer = ImovelPublicSerializer(base_queryset, many=True)
        
        # Adiciona a mensagem de sucesso à resposta
        mensagem_resposta = "Resultados da sua pesquisa com IA."
        if not base_queryset.exists():
            mensagem_resposta = "Não encontrei nenhum imóvel que corresponda à sua procura. Tente refinar a sua pesquisa."

        return Response({
            "mensagem": mensagem_resposta,
            "imoveis": serializer.data
        }, status=status.HTTP_200_OK)


# ===================================================================
# VIEWS INTERNAS (Para o painel administrativo, requerem login)
# ===================================================================

class ImovelViewSet(viewsets.ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['logradouro', 'cidade', 'titulo_anuncio', 'codigo_referencia']

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
                base_queryset = base_queryset.exclude(status=Imovel.Status.DESATIVADO)
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
            instance.status = Imovel.Status.DESATIVADO
            instance.save()
        else:
            raise PermissionDenied("Você não tem permissão para inativar este imóvel.")


class ImagemImovelViewSet(viewsets.ModelViewSet):
    queryset = ImagemImovel.objects.all()
    serializer_class = ImagemImovelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ImagemImovel.objects.all()
        if self.request.tenant:
            return ImagemImovel.objects.filter(imovel__imobiliaria=self.request.tenant)
        return ImagemImovel.objects.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        imovel_id = request.data.get('imovel')
        if not imovel_id:
            return Response({'imovel': ['O ID do imóvel é obrigatório.']}, status=status.HTTP_400_BAD_REQUEST)

        imovel = get_object_or_404(Imovel, pk=imovel_id)
        if not (request.user.is_superuser or (hasattr(request.user, 'perfil') and imovel.imobiliaria == request.tenant)):
            raise PermissionDenied("Você não tem permissão para adicionar imagens a este imóvel.")

        imagens = request.FILES.getlist('imagem')
        if not imagens:
            return Response({'imagem': ['Nenhuma imagem foi enviada.']}, status=status.HTTP_400_BAD_REQUEST)

        max_ordem_result = ImagemImovel.objects.filter(imovel=imovel).aggregate(Max('ordem'))
        max_ordem = max_ordem_result['ordem__max'] if max_ordem_result['ordem__max'] is not None else -1

        new_images = []
        for index, imagem in enumerate(imagens):
            nova_ordem = max_ordem + 1 + index
            new_images.append(ImagemImovel(
                imovel=imovel,
                imagem=imagem,
                ordem=nova_ordem,
                principal=(nova_ordem == 0)
            ))
        
        ImagemImovel.objects.bulk_create(new_images)
        
        if ImagemImovel.objects.filter(imovel=imovel, principal=True).count() > 1:
            ImagemImovel.objects.filter(imovel=imovel).exclude(pk=new_images[0].pk).update(principal=False)
        
        return Response({'status': f'{len(new_images)} imagens foram carregadas com sucesso.'}, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
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
                assunto = f"Novo Contato para o Imóvel: {contato.imovel.logradouro}"
                mensagem_corpo = f"""
                Você recebeu um novo contato através do site!
                Imóvel: {contato.imovel.logradouro} (ID: {contato.imovel.id})
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
                    mensagem=f"Novo contato de '{contato.nome}' para o imóvel '{contato.imovel.logradouro}'.",
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
        finalidade_texto = "venda" if imovel.status == Imovel.Status.A_VENDA else "locação"
        valor = imovel.valor_venda if imovel.status == Imovel.Status.A_VENDA else imovel.valor_aluguel
        valor = valor or Decimal(0)
        reais = int(valor)
        centavos = int((valor - reais) * 100)
        valor_por_extenso = num2words(reais, lang='pt_BR') + " reais"
        if centavos > 0:
            valor_por_extenso += " e " + num2words(centavos, lang='pt_BR') + " centavos"
        
        # CORRIGIDO: Adicionada lógica para obter o nome correto do proprietário.
        proprietario = imovel.proprietario
        nome_proprietario = proprietario.razao_social if proprietario.tipo_pessoa == 'JURIDICA' and proprietario.razao_social else proprietario.nome

        context = {
            'imovel': imovel,
            'proprietario': proprietario,
            'nome_proprietario': nome_proprietario, # Passa o nome correto para o template
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
        base_queryset = Imovel.objects.filter(imobiliaria=tenant).exclude(status=Imovel.Status.DESATIVADO)
        sumario = base_queryset.aggregate(
            expirando_em_30_dias=Count('id', filter=Q(data_fim_autorizacao__gte=hoje, data_fim_autorizacao__lte=limite_30_dias)),
            expiradas_recentemente=Count('id', filter=Q(data_fim_autorizacao__lt=hoje, data_fim_autorizacao__gte=limite_passado_30_dias)),
            ativas=Count('id', filter=Q(data_fim_autorizacao__gte=hoje)),
            sem_data=Count('id', filter=Q(data_fim_autorizacao__isnull=True)),
        )

        # CORRIGIDO: Utiliza a anotação Case/When para obter o nome correto do proprietário.
        imoveis_com_status = base_queryset.annotate(
            status_autorizacao_display=Case(
                When(data_fim_autorizacao__isnull=True, then=Value('Incompleto')),
                When(data_fim_autorizacao__lt=hoje, then=Value('Expirado')),
                When(data_fim_autorizacao__lte=limite_30_dias, then=Value('Expirando')),
                default=Value('Ativo'),
                output_field=CharField(),
            ),
            proprietario_nome_display=Case(
                When(proprietario__tipo_pessoa='JURIDICA', then='proprietario__razao_social'),
                default='proprietario__nome',
                output_field=CharField()
            )
        ).values(
            'id', 'codigo_referencia', 'titulo_anuncio', 'proprietario_nome_display',
            'data_captacao', 'data_fim_autorizacao', 'status_autorizacao_display'
        )

        data = {
            'sumario': sumario,
            'imoveis': list(imoveis_com_status)
        }
        return Response(data)

class ImobiliariaPublicDetailView(RetrieveAPIView):
    queryset = Imobiliaria.objects.all()
    serializer_class = ImobiliariaPublicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'subdominio'
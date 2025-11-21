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
from django.http import HttpResponse, QueryDict, Http404 
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Count, Q, Case, When, Value, CharField, Max, F, ExpressionWrapper, fields
from datetime import date, timedelta
from io import BytesIO
from xhtml2pdf import pisa
import locale
from num2words import num2words
from decimal import Decimal, InvalidOperation
import json
import requests
import google.generativeai as genai
import os
from django.conf import settings
from django.db.models.fields import DecimalField, IntegerField, CharField, BooleanField

from rest_framework.request import Request as DRFRequest
from django.test import RequestFactory


from .models import Imovel, ImagemImovel, ContatoImovel
from .serializers import (
    ImovelSerializer, 
    ImovelPublicSerializer, 
    ContatoImovelSerializer, 
    ImagemImovelSerializer,
    ImovelSimplificadoSerializer # Importação adicionada aqui
)
from core.models import Imobiliaria, PerfilUsuario, Notificacao
from app_clientes.models import Oportunidade
from app_config_ia.models import ModeloDePrompt
from core.serializers import ImobiliariaPublicSerializer

# Configura a API do Google Gemini
try:
    api_key=os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("AVISO: GOOGLE_API_KEY não encontrada nas variáveis de ambiente.")
    else:
        genai.configure(api_key=api_key)
except Exception as e:
    print(f"Erro ao configurar a API do Google: {e}")


# ===================================================================
# VIEWS PÚBLICAS (Mantidas como estavam)
# ===================================================================

class ImovelPublicListView(ListAPIView):
    serializer_class = ImovelPublicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        subdomain_param = self.request.query_params.get('subdomain', None)
        finalidade = self.request.query_params.get('finalidade', None)
        tipo = self.request.query_params.get('tipo', None)
        cidade = self.request.query_params.get('cidade', None)
        valor_min = self.request.query_params.get('valor_min', None)
        valor_max = self.request.query_params.get('valor_max', None)
        quartos_min = self.request.query_params.get('quartos_min', None)
        vagas_min = self.request.query_params.get('vagas_min', None)
        status_param = self.request.query_params.get('status', None)
        aceita_pet = self.request.query_params.get('aceita_pet', None)
        mobiliado = self.request.query_params.get('mobiliado', None)
        piscina = self.request.query_params.get('piscina', None)

        imobiliaria_obj = None

        if self.request.user.is_authenticated and self.request.tenant:
            imobiliaria_obj = self.request.tenant
        elif subdomain_param:
            try:
                imobiliaria_obj = Imobiliaria.objects.get(subdominio__iexact=subdomain_param)
            except Imobiliaria.DoesNotExist:
                return Imovel.objects.none()

        if not imobiliaria_obj:
            return Imovel.objects.none()

        base_queryset = Imovel.objects.filter(imobiliaria=imobiliaria_obj)

        if not self.request.user.is_authenticated:
            base_queryset = base_queryset.filter(publicado_no_site=True)
            if not status_param:
                base_queryset = base_queryset.exclude(status='DESATIVADO')
            else:
                base_queryset = base_queryset.filter(status=status_param) 
        else:
             if not status_param:
                 base_queryset = base_queryset.exclude(status='DESATIVADO')
             else:
                 base_queryset = base_queryset.filter(status=status_param)

        if finalidade: base_queryset = base_queryset.filter(finalidade=finalidade)
        if tipo: base_queryset = base_queryset.filter(tipo=tipo)
        if cidade: base_queryset = base_queryset.filter(cidade__icontains=cidade)
        if valor_min:
            q_filter = Q(valor_venda__gte=valor_min) if finalidade == 'A_VENDA' else Q(valor_aluguel__gte=valor_min)
            base_queryset = base_queryset.filter(q_filter)
        if valor_max:
            q_filter = Q(valor_venda__lte=valor_max) if finalidade == 'A_VENDA' else Q(valor_aluguel__lte=valor_max)
            base_queryset = base_queryset.filter(q_filter)
        if quartos_min: base_queryset = base_queryset.filter(quartos__gte=quartos_min)
        if vagas_min: base_queryset = base_queryset.filter(vagas_garagem__gte=vagas_min)
        if aceita_pet: base_queryset = base_queryset.filter(aceita_pet=True)
        if mobiliado: base_queryset = base_queryset.filter(mobiliado=True)
        if piscina: base_queryset = base_queryset.filter(Q(piscina_privativa=True) | Q(piscina_condominio=True))
        if status_param:
             base_queryset = base_queryset.filter(status=status_param)

        return base_queryset


class ImovelPublicDetailView(RetrieveAPIView):
    serializer_class = ImovelPublicSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Imovel.objects.filter(publicado_no_site=True) 
    lookup_field = 'pk'

    def get_queryset(self):
        qs = super().get_queryset()
        subdomain = self.request.query_params.get('subdomain')

        if not subdomain:
             return qs.none()

        try:
            imobiliaria_obj = Imobiliaria.objects.get(subdominio__iexact=subdomain)
            return qs.filter(imobiliaria=imobiliaria_obj)
        except Imobiliaria.DoesNotExist:
            return qs.none()


class ImovelIAView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        user_query = request.data.get('query')
        subdomain_param = request.query_params.get('subdomain', None)

        if not user_query:
            return Response({"error": "O campo 'query' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        imobiliaria_obj = None
        if self.request.tenant:
             imobiliaria_obj = self.request.tenant
        elif subdomain_param:
            try:
                imobiliaria_obj = Imobiliaria.objects.get(subdominio__iexact=subdomain_param)
            except Imobiliaria.DoesNotExist:
                return Response({
                    "mensagem": "Imobiliária não encontrada.",
                    "imoveis": []
                }, status=status.HTTP_404_NOT_FOUND)

        if not imobiliaria_obj:
             return Response({
                "mensagem": "Subdomínio da imobiliária não fornecido.",
                "imoveis": []
             }, status=status.HTTP_400_BAD_REQUEST)

        try:
            prompt_config = ModeloDePrompt.objects.get(em_uso_busca=True)
            template_prompt = prompt_config.template_do_prompt
        except ModeloDePrompt.DoesNotExist:
            return Response(
                {"error": "Nenhum modelo de prompt para busca por IA está ativo."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        prompt_final = template_prompt.replace('{{user_query}}', user_query)

        try:
            model_name = 'models/gemini-flash-latest' 
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt_final)

            if not response.parts:
                 raise ValueError("Resposta inesperada da IA.")

            json_text_raw = response.parts[0].text
            json_text = json_text_raw.strip().lstrip('```json').rstrip('```').strip()
            search_params = json.loads(json_text)

        except json.JSONDecodeError as json_err:
             return Response(
                 {"error": f"A IA retornou uma resposta em formato inválido. Tente novamente."},
                 status=status.HTTP_503_SERVICE_UNAVAILABLE
             )
        except Exception as e:
            if "is not found" in str(e) or "is not supported" in str(e):
                 error_message = f"O modelo de IA '{model_name}' não está disponível. Tente outro modelo ou verifique sua API Key. ({e})"
            else:
                 error_message = f"Não consegui interpretar a sua pesquisa. Tente ser mais específico. ({e})"
            return Response({"error": error_message}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        base_queryset = Imovel.objects.filter(
            imobiliaria=imobiliaria_obj,
            publicado_no_site=True
        ).exclude(status=Imovel.Status.DESATIVADO)

        if search_params.get('busca_valida') == False:
            mensagem_vaga = search_params.get('mensagem_resposta', "Não consegui identificar parâmetros de busca válidos. Por favor, especifique o que você procura.")
            return Response({
                 "mensagem": mensagem_vaga,
                 "imoveis": []
            }, status=status.HTTP_200_OK)
        
        status_filtro_ia = search_params.get('status', None)
        if status_filtro_ia:
             if status_filtro_ia in Imovel.Status.values:
                 base_queryset = base_queryset.filter(status=status_filtro_ia)

        if 'finalidade' in search_params:
            finalidade_param = search_params['finalidade']
            if finalidade_param in Imovel.Finalidade.values:
                base_queryset = base_queryset.filter(finalidade=finalidade_param)

        if 'tipo' in search_params:
            tipo_param = search_params['tipo'].upper()
            if hasattr(Imovel.TipoImovel, tipo_param):
                base_queryset = base_queryset.filter(tipo=tipo_param)

        if 'cidade' in search_params:
            base_queryset = base_queryset.filter(cidade__icontains=search_params['cidade'])

        if 'bairro' in search_params:
            bairro_param = search_params['bairro']
            if bairro_param and isinstance(bairro_param, str):
                base_queryset = base_queryset.filter(bairro__icontains=bairro_param)

        if 'valor_min' in search_params:
            valor_min_ia = search_params['valor_min']
            try:
                valor_min_decimal = Decimal(valor_min_ia)
                q_filter_min = Q(valor_venda__gte=valor_min_decimal) if status_filtro_ia == Imovel.Status.A_VENDA else Q(valor_aluguel__gte=valor_min_decimal)
                if not status_filtro_ia: 
                    q_filter_min = Q(valor_venda__gte=valor_min_decimal) | Q(valor_aluguel__gte=valor_min_decimal)
                base_queryset = base_queryset.filter(q_filter_min)
            except (ValueError, TypeError, InvalidOperation):
                 pass 

        if 'valor_max' in search_params:
            valor_max_ia = search_params['valor_max']
            try:
                 valor_max_decimal = Decimal(valor_max_ia)
                 q_filter_max = Q(valor_venda__lte=valor_max_decimal) if status_filtro_ia == Imovel.Status.A_VENDA else Q(valor_aluguel__lte=valor_max_decimal)
                 if not status_filtro_ia:
                      q_filter_max = Q(valor_venda__lte=valor_max_decimal) | Q(valor_aluguel__lte=valor_max_decimal)
                 base_queryset = base_queryset.filter(q_filter_max)
            except (ValueError, TypeError, InvalidOperation):
                 pass 

        if 'quartos_min' in search_params:
            try:
                 quartos_min_ia = int(search_params['quartos_min'])
                 if quartos_min_ia >= 0:
                      base_queryset = base_queryset.filter(quartos__gte=quartos_min_ia)
            except (ValueError, TypeError):
                 pass 

        if 'vagas_min' in search_params:
            try:
                 vagas_min_ia = int(search_params['vagas_min'])
                 if vagas_min_ia >= 0:
                      base_queryset = base_queryset.filter(vagas_garagem__gte=vagas_min_ia)
            except (ValueError, TypeError):
                 pass
        
        if 'banheiros_min' in search_params:
            try:
                 banheiros_min_ia = int(search_params['banheiros_min'])
                 if banheiros_min_ia >= 0:
                      base_queryset = base_queryset.filter(banheiros__gte=banheiros_min_ia) 
            except (ValueError, TypeError):
                 pass
        
        if 'suites_min' in search_params:
            try:
                 suites_min_ia = int(search_params['suites_min'])
                 if suites_min_ia >= 0:
                      base_queryset = base_queryset.filter(suites__gte=suites_min_ia) 
            except (ValueError, TypeError):
                 pass

        if 'andar_min' in search_params:
            try:
                 andar_min_ia = int(search_params['andar_min'])
                 if andar_min_ia >= 0:
                      base_queryset = base_queryset.filter(andar__gte=andar_min_ia) 
            except (ValueError, TypeError):
                 pass

        if 'area_min' in search_params:
            try:
                 area_min_ia = Decimal(search_params['area_min'])
                 if area_min_ia > 0:
                      base_queryset = base_queryset.filter(
                           Q(area_util__gte=area_min_ia) | 
                           Q(area_construida__gte=area_min_ia)
                      )
            except (ValueError, TypeError, InvalidOperation):
                 pass

        if search_params.get('aceita_pet') == True:
            base_queryset = base_queryset.filter(aceita_pet=True)
        if search_params.get('mobiliado') == True:
            base_queryset = base_queryset.filter(mobiliado=True)
        if search_params.get('piscina') == True:
            base_queryset = base_queryset.filter(Q(piscina_privativa=True) | Q(piscina_condominio=True))
        if search_params.get('ar_condicionado') == True:
             base_queryset = base_queryset.filter(ar_condicionado=True)
        if search_params.get('salao_festas') == True:
             base_queryset = base_queryset.filter(salao_festas=True)
        if search_params.get('elevador') == True:
             base_queryset = base_queryset.filter(elevador=True)

        serializer = ImovelPublicSerializer(base_queryset, many=True)
        mensagem_resposta = search_params.get('mensagem_resposta', "Resultados da sua pesquisa com IA.")
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
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    
    # CORREÇÃO: Adicionado campos do proprietário para busca
    search_fields = [
        'logradouro', 'cidade', 'titulo_anuncio', 'codigo_referencia', 'bairro',
        'proprietario__nome', 'proprietario__razao_social', 'proprietario__documento'
    ] 

    def get_queryset(self):
        # 1. Filtro base por Tenant
        if self.request.user.is_superuser:
             base_queryset = Imovel.objects.all()
        elif self.request.tenant:
            base_queryset = Imovel.objects.filter(imobiliaria=self.request.tenant)
        else:
            return Imovel.objects.none()

        # 2. NÃO aplicar filtros de query param se for a action 'lista_simples'
        if self.action == 'lista_simples':
            return base_queryset 

        # 3. Aplicar filtros de query param para as actions normais (list, retrieve, etc.)
        status_param = self.request.query_params.get('status', None)
        
        if status_param:
             if status_param in Imovel.Status.values:
                base_queryset = base_queryset.filter(status=status_param)
        elif self.action == 'list': 
             base_queryset = base_queryset.exclude(status=Imovel.Status.DESATIVADO)

        finalidade = self.request.query_params.get('finalidade', None) 
        tipo = self.request.query_params.get('tipo', None)
        cidade = self.request.query_params.get('cidade', None)
        bairro = self.request.query_params.get('bairro', None)
        proprietario_id = self.request.query_params.get('proprietario', None)


        if finalidade: base_queryset = base_queryset.filter(finalidade=finalidade)
        if tipo: base_queryset = base_queryset.filter(tipo=tipo)
        if cidade: base_queryset = base_queryset.filter(cidade__icontains=cidade)
        if bairro: base_queryset = base_queryset.filter(bairro__icontains=bairro)
        
        if proprietario_id:
            base_queryset = base_queryset.filter(proprietario_id=proprietario_id)
            
        return base_queryset.order_by('-data_atualizacao')

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
        instance = serializer.instance
        if self.request.user.is_superuser or (self.request.tenant and instance.imobiliaria == self.request.tenant):
             serializer.save()
        else:
             raise PermissionDenied("Você não tem permissão para atualizar este imóvel.")

    def perform_destroy(self, instance):
        if self.request.user.is_superuser or (self.request.tenant and instance.imobiliaria == self.request.tenant):
             instance.status = Imovel.Status.DESATIVADO
             instance.publicado_no_site = False
             instance.save()
             return Response(status=status.HTTP_200_OK)
        else:
             raise PermissionDenied("Você não tem permissão para inativar este imóvel.")

    # ==================================================================
    # AÇÃO 'lista_simples'
    # ==================================================================
    @action(detail=False, methods=['get'], url_path='lista-simples')
    def lista_simples(self, request):
        """
        Retorna uma lista simplificada de imóveis para uso em dropdowns.
        """
        queryset = self.get_queryset()
        # Aqui usamos o serializer que criamos e importamos localmente
        serializer = ImovelSimplificadoSerializer(queryset, many=True)
        return Response(serializer.data)

    def _get_imovel_contexto_para_ia(self, imovel):
        """Helper para formatar os dados do imóvel para a IA."""
        
        contexto = []
        contexto.append(f"Tipo de Imóvel: {imovel.get_tipo_display()}")
        contexto.append(f"Finalidade: {imovel.get_finalidade_display()}") 
        contexto.append(f"Status: {imovel.get_status_display()}")
        contexto.append(f"Localização: Bairro {imovel.bairro}, {imovel.cidade} - {imovel.estado}")
        
        if imovel.valor_venda and imovel.status == Imovel.Status.A_VENDA:
            contexto.append(f"Valor de Venda: R$ {imovel.valor_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        if imovel.valor_aluguel and imovel.status == Imovel.Status.PARA_ALUGAR:
            contexto.append(f"Valor de Aluguel: R$ {imovel.valor_aluguel:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        if imovel.valor_condominio:
            contexto.append(f"Condomínio: R$ {imovel.valor_condominio:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        contexto.append(f"Área Útil: {imovel.area_util or imovel.area_construida or 'Não informado'} m²")
        
        divisoes = []
        if imovel.quartos: divisoes.append(f"{imovel.quartos} quarto(s)")
        if imovel.suites: divisoes.append(f"{imovel.suites} suíte(s)")
        if imovel.banheiros: divisoes.append(f"{imovel.banheiros} banheiro(s)")
        if imovel.vagas_garagem: divisoes.append(f"{imovel.vagas_garagem} vaga(s) de garagem")
        if divisoes:
            contexto.append(f"Divisões: {', '.join(divisoes)}.")

        caracteristicas = []
        if imovel.mobiliado: caracteristicas.append("Mobiliado")
        if imovel.moveis_planejados: caracteristicas.append("Móveis Planejados")
        if imovel.piscina_privativa: caracteristicas.append("Piscina Privativa")
        if imovel.churrasqueira_privativa: caracteristicas.append("Churrasqueira Privativa")
        if imovel.ar_condicionado: caracteristicas.append("Ar Condicionado")
        if imovel.varanda: caracteristicas.append("Varanda/Sacada")
        if imovel.piscina_condominio: caracteristicas.append("Piscina no Condomínio")
        if imovel.academia: caracteristicas.append("Academia no Condomínio")
        if imovel.salao_festas: caracteristicas.append("Salão de Festas")
        if imovel.playground: caracteristicas.append("Playground")
        if imovel.portaria_24h: caracteristicas.append("Portaria 24h")
        if imovel.elevador: caracteristicas.append("Elevador")
        if caracteristicas:
            contexto.append(f"Destaques: {', '.join(caracteristicas)}.")

        return "\n".join(contexto)

    @action(detail=True, methods=['post'], url_path='gerar-descricao-ia')
    def gerar_descricao_ia(self, request, pk=None):
        try:
            imovel = self.get_object()
        except Exception as e:
             return Response({"error": f"Imóvel não encontrado: {e}"}, status=status.HTTP_404_NOT_FOUND)

        try:
            prompt_config = ModeloDePrompt.objects.get(em_uso_descricao=True)
            template_prompt = prompt_config.template_do_prompt
        except ModeloDePrompt.DoesNotExist:
            return Response(
                {"error": "Nenhum modelo de prompt para 'Geração de Descrição' está ativo no sistema."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        voz_da_marca_obj = imovel.imobiliaria.voz_da_marca_preferida
        if voz_da_marca_obj:
            voz_da_marca = str(voz_da_marca_obj)
        else:
            voz_da_marca = "um tom profissional e convidativo"
        
        imovel_data = self._get_imovel_contexto_para_ia(imovel)
        
        prompt_final = template_prompt.replace('{{imovel_data}}', imovel_data)
        prompt_final = prompt_final.replace('{{voz_da_marca}}', voz_da_marca)

        try:
            if not api_key:
                 raise ValueError("GOOGLE_API_KEY não está configurada no servidor.")

            model_name = 'models/gemini-flash-latest'
            model = genai.GenerativeModel(model_name)
            generation_config = genai.types.GenerationConfig(temperature=0.7)
            response = model.generate_content(prompt_final, generation_config=generation_config)

            if not response.parts:
                 raise ValueError("Resposta inesperada da IA.")

            generated_text = response.parts[0].text
            generated_text = generated_text.strip().lstrip('```markdown').lstrip('```').rstrip('```').strip()
            
            prefixo = 'título sugerido:'
            if generated_text.lower().startswith(prefixo):
                 if '\n' in generated_text:
                     generated_text = generated_text.split('\n', 1)[1].strip()
                 else:
                     generated_text = generated_text[len(prefixo):].lstrip(':').strip()
            generated_text = generated_text.strip()

            return Response({'descricao': generated_text}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"DEBUG: Erro na API do Google Gemini durante a geração de descrição: {e}")
            return Response({"error": f"Erro ao comunicar com a IA: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


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

        try:
            if request.user.is_superuser:
                 imovel = Imovel.objects.get(pk=imovel_id)
            elif request.tenant:
                 imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=request.tenant)
            else:
                 raise PermissionDenied("Tenant não identificado.")
        except Imovel.DoesNotExist:
             raise Http404("Imóvel não encontrado ou não pertence à sua imobiliária.")


        imagens = request.FILES.getlist('imagem')
        if not imagens:
            return Response({'imagem': ['Nenhuma imagem foi enviada.']}, status=status.HTTP_400_BAD_REQUEST)

        max_ordem_result = ImagemImovel.objects.filter(imovel=imovel).aggregate(Max('ordem'))
        max_ordem = max_ordem_result['ordem__max'] if max_ordem_result['ordem__max'] is not None else -1

        new_images = []
        make_first_principal = not ImagemImovel.objects.filter(imovel=imovel, principal=True).exists()

        for index, imagem in enumerate(imagens):
            nova_ordem = max_ordem + 1 + index
            is_principal = make_first_principal and index == 0
            new_images.append(ImagemImovel(
                imovel=imovel,
                imagem=imagem,
                ordem=nova_ordem,
                principal=is_principal
            ))

        created_images = ImagemImovel.objects.bulk_create(new_images)
        serializer = self.get_serializer(created_images, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def perform_destroy(self, instance):
        if not (self.request.user.is_superuser or (self.request.tenant and instance.imovel.imobiliaria == self.request.tenant)):
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
        imovel_id = request.data.get('imovel_id')

        if not ordem_ids or not imovel_id:
            return Response({'detail': 'A lista de IDs de imagem e o ID do imóvel são necessários.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if request.user.is_superuser:
                 imovel = Imovel.objects.get(pk=imovel_id)
            elif request.tenant:
                 imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=request.tenant)
            else:
                 raise PermissionDenied("Tenant não identificado.")
        except Imovel.DoesNotExist:
             raise Http404("Imóvel não encontrado ou não pertence à sua imobiliária.")


        imagens_qs = ImagemImovel.objects.filter(imovel=imovel, id__in=ordem_ids)
        imagens_map = {img.id: img for img in imagens_qs}

        if len(ordem_ids) != len(imagens_map):
             raise PermissionDenied("Uma ou mais imagens fornecidas são inválidas ou não pertencem a este imóvel.")

        updated_instances = []
        for index, image_id_str in enumerate(ordem_ids):
            image_id = int(image_id_str)
            if image_id in imagens_map: 
                img = imagens_map[image_id]
                img.ordem = index
                img.principal = (index == 0)
                updated_instances.append(img)
            else:
                 print(f"Alerta CRÍTICO: ID de imagem {image_id} não encontrado no mapeamento durante reordenação, APÓS validação inicial.")

        ImagemImovel.objects.bulk_update(updated_instances, ['ordem', 'principal'])
        return Response({'status': 'Ordem das imagens atualizada com sucesso.'}, status=status.HTTP_200_OK)


class ContatoImovelViewSet(viewsets.ModelViewSet):
    queryset = ContatoImovel.objects.all()
    serializer_class = ContatoImovelSerializer

    def get_permissions(self):
        # Permite acesso irrestrito para CRIAR (POST)
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy', 'arquivar']:
            self.permission_classes = [permissions.IsAuthenticated]
        else: # create
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def get_queryset(self):
        # CORREÇÃO: Adicionar select_related('imovel') para popular o imovel_obj no serializer
        base_queryset = ContatoImovel.objects.filter(arquivado=False).select_related('imovel')
        
        if self.request.user.is_superuser:
            return base_queryset.all().order_by('-data_contato')
        elif self.request.user.is_authenticated and self.request.tenant:
            return base_queryset.filter(imovel__imobiliaria=self.request.tenant).order_by('-data_contato')
        return ContatoImovel.objects.none()

    def perform_create(self, serializer):
        contato = serializer.save()
        try:
            imobiliaria = contato.imovel.imobiliaria
            if hasattr(imobiliaria, 'email_contato') and imobiliaria.email_contato:
                destinatario_email = imobiliaria.email_contato
                assunto = f"Novo Contato para o Imóvel: {contato.imovel.titulo_anuncio or contato.imovel.logradouro}"
                base_url_painel = "http://localhost:5173" # Ou a URL de produção
                link_imovel_painel = f"{base_url_painel}/imoveis/editar/{contato.imovel.id}"

                mensagem_corpo = f"""
                Você recebeu um novo contato através do site!
                ...
                """
                remetente = settings.DEFAULT_FROM_EMAIL
                send_mail(assunto, mensagem_corpo, remetente, [destinatario_email], fail_silently=False)

            oportunidade_associada = Oportunidade.objects.filter(imovel=contato.imovel).first()
            if oportunidade_associada and oportunidade_associada.responsavel:
                # CORREÇÃO: O responsável já é o objeto User.
                destinatario_notificacao = oportunidade_associada.responsavel 
                Notificacao.objects.create(
                    destinatario=destinatario_notificacao,
                    mensagem=f"Novo contato de '{contato.nome}' para o imóvel '{contato.imovel.titulo_anuncio or contato.imovel.logradouro}'.",
                    link=f"/contatos" 
                )
        except Exception as e:
            print(f"ERRO AO ENVIAR NOTIFICAÇÕES DE CONTATO: {e}")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def arquivar(self, request, pk=None):
        contato = self.get_object()
        contato.arquivado = True
        contato.save()
        return Response({'status': 'Contacto arquivado com sucesso'}, status=status.HTTP_200_OK)


class GerarAutorizacaoPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_imovel_data(self, request, imovel_id):
        try:
            if request.user.is_superuser:
                 imovel = Imovel.objects.get(pk=imovel_id)
            elif request.tenant:
                 imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=request.tenant)
            else:
                 raise PermissionDenied("Tenant não identificado para o usuário autenticado.")
        except Imovel.DoesNotExist:
             raise Http404("Imóvel não encontrado ou não pertence à sua imobiliária.")

        if not imovel.proprietario:
            raise ValueError("Erro: O imóvel não possui um proprietário vinculado.")
        return imovel

    def _processar_pdf(self, request, imovel, comissao, data_fim, info_adicionais):
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except locale.Error:
            try:
                 locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
            except locale.Error:
                 pass 

        hoje = date.today()
        finalidade_texto = imovel.get_finalidade_display() 
        valor = imovel.valor_venda if imovel.status == Imovel.Status.A_VENDA else imovel.valor_aluguel
        valor = valor or Decimal(0)
        reais = int(valor)
        centavos = int((valor - reais) * 100)
        
        try:
            valor_por_extenso = num2words(reais, lang='pt_BR') + " reais"
            if centavos > 0:
                 valor_por_extenso += " e " + num2words(centavos, lang='pt_BR') + " centavos"
        except NotImplementedError:
             valor_por_extenso = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
             
        try:
            comissao_por_extenso = num2words(float(comissao), lang='pt_BR') + " por cento"
        except NotImplementedError:
             comissao_por_extenso = f"{comissao}%"

        proprietario = imovel.proprietario
        nome_proprietario = proprietario.razao_social if proprietario.tipo_pessoa == 'JURIDICA' and proprietario.razao_social else proprietario.nome

        context = {
            'imovel': imovel,
            'proprietario': proprietario,
            'nome_proprietario': nome_proprietario,
            'imobiliaria': imovel.imobiliaria,
            'finalidade_texto': finalidade_texto,
            'valor': valor,
            'valor_por_extenso': valor_por_extenso,
            'comissao_percentual': comissao, 
            'comissao_por_extenso': comissao_por_extenso,
            'informacoes_adicionais': info_adicionais, 
            'data_hoje': hoje,
            'dia_hoje': hoje.day,
            'mes_hoje': hoje.strftime("%B"),
            'ano_hoje': hoje.year,
            'data_fim_autorizacao_formatada': data_fim.strftime("%d de %B de %Y") if data_fim else "INDETERMINADO"
        }
        
        html_string = render_to_string('autorizacao_template.html', context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result, encoding='UTF-8')

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            status_texto = imovel.get_status_display().lower().replace(" ", "_")
            filename = f'autorizacao_{status_texto}_imovel_{imovel.codigo_referencia or imovel.id}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
             return HttpResponse(f"Erro ao gerar o PDF: {pdf.err}", status=500)

    def get(self, request, imovel_id, *args, **kwargs):
        try:
            imovel = self._get_imovel_data(request, imovel_id)
            comissao_default = imovel.comissao_percentual or Decimal(0)
            data_fim_default = imovel.data_fim_autorizacao
            info_adicionais_default = imovel.informacoes_adicionais_autorizacao or ''

            return self._processar_pdf(
                request, 
                imovel, 
                comissao_default, 
                data_fim_default, 
                info_adicionais_default
            )
        except Http404:
             return HttpResponse("Imóvel não encontrado.", status=404)
        except PermissionDenied as e:
            # CORREÇÃO DO SYNTAXERROR (4G03 -> 403):
             return HttpResponse(f"Erro de Permissão: {e}", status=403)
        except ValueError as e: 
             return HttpResponse(str(e), status=400)
        except Exception as e:
            return HttpResponse(f"Erro interno ao gerar PDF: {e}", status=500)

    def post(self, request, imovel_id, *args, **kwargs):
        try:
            imovel = self._get_imovel_data(request, imovel_id)
            data = request.data
            
            comissao = imovel.comissao_percentual or Decimal(0)
            try:
                 comissao = Decimal(str(data.get('comissao_percentual', comissao)))
            except (InvalidOperation, TypeError):
                 pass 
                 
            data_fim = imovel.data_fim_autorizacao 
            data_fim_str = data.get('data_fim_autorizacao')
            if data_fim_str:
                 try:
                     data_fim = date.fromisoformat(data_fim_str)
                 except ValueError:
                     pass 
                 
            info_adicionais = data.get(
                'informacoes_adicionais', 
                imovel.informacoes_adicionais_autorizacao or ''
            )

            return self._processar_pdf(
                request, 
                imovel, 
                comissao, 
                data_fim, 
                info_adicionais
            )
        except Http404:
             return HttpResponse("Imóvel não encontrado.", status=404)
        except PermissionDenied as e:
             return HttpResponse(f"Erro de Permissão: {e}", status=403)
        except ValueError as e: 
             return HttpResponse(str(e), status=400)
        except Exception as e:
            return HttpResponse(f"Erro interno ao gerar PDF: {e}", status=500)


class AutorizacaoStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser] 

    def get(self, request, *args, **kwargs):
        tenant = request.tenant
        if not tenant and request.user.is_superuser:
             tenant = Imobiliaria.objects.first() 
        if not tenant:
            return Response({"error": "Nenhuma imobiliária associada ou selecionada."}, status=status.HTTP_400_BAD_REQUEST)

        hoje = timezone.now().date()
        limite_30_dias = hoje + timedelta(days=30)
        limite_passado_30_dias = hoje - timedelta(days=30)

        base_queryset = Imovel.objects.filter(imobiliaria=tenant).exclude(status=Imovel.Status.DESATIVADO)

        sumario = base_queryset.aggregate(
            expirando_em_30_dias=Count('id', filter=Q(data_fim_autorizacao__gte=hoje, data_fim_autorizacao__lte=limite_30_dias)),
            expiradas_recentemente=Count('id', filter=Q(data_fim_autorizacao__lt=hoje, data_fim_autorizacao__gte=limite_passado_30_dias)),
            ativas=Count('id', filter=Q(data_fim_autorizacao__gte=hoje)),
            expiradas_total=Count('id', filter=Q(data_fim_autorizacao__lt=hoje)),
            sem_data=Count('id', filter=Q(data_fim_autorizacao__isnull=True)),
            total_imoveis_ativos=Count('id')
        )

        imoveis_com_status = base_queryset.annotate(
            status_autorizacao_display=Case(
                When(data_fim_autorizacao__isnull=True, then=Value('Sem Data')),
                When(data_fim_autorizacao__lt=hoje, then=Value('Expirado')),
                When(data_fim_autorizacao__lte=limite_30_dias, then=Value('Expirando')),
                default=Value('Ativo'),
                output_field=CharField(),
            ),
            proprietario_nome_display=Case(
                When(proprietario__isnull=False, proprietario__tipo_pessoa='JURIDICA', then='proprietario__razao_social'),
                When(proprietario__isnull=False, proprietario__tipo_pessoa='FISICA', then='proprietario__nome'),
                default=Value('Proprietário não vinculado'),
                output_field=CharField()
            )
        ).values(
            'id', 'codigo_referencia', 'titulo_anuncio', 'proprietario_nome_display',
            'data_captacao', 'data_fim_autorizacao', 'status_autorizacao_display'
        ).order_by('data_fim_autorizacao')

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
    lookup_url_kwarg = 'pk'

    def get_object(self):
        subdomain_from_url = self.kwargs.get(self.lookup_url_kwarg)

        if not subdomain_from_url:
            raise Http404("Argumento de subdomínio não encontrado na URL.")

        queryset = self.filter_queryset(self.get_queryset())

        try:
            filter_kwargs = {f"{self.lookup_field}__iexact": subdomain_from_url}
            obj = queryset.filter(**filter_kwargs).first()

            if obj is None:
                 raise Http404("No Imobiliaria matches the given query.")

            self.check_object_permissions(self.request, obj)
            return obj
        except Exception as e:
             print(f"Erro inesperado ao buscar imobiliária: {e}") 
             raise Http404("Erro ao buscar dados da imobiliária.")

# --- INÍCIO DA IMPLEMENTAÇÃO DO RELATÓRIO DE AUTORIZAÇÕES (JSON + PDF) ---

def _get_autorizacao_queryset(query_params):
    """
    Helper reutilizável para buscar e filtrar o queryset de autorizações.
    Usado tanto pela API JSON quanto pela geração de PDF.
    """
    queryset = Imovel.objects.filter(
        data_fim_autorizacao__isnull=False
    ).select_related('proprietario')

    today = date.today()
    
    dias_timedelta = ExpressionWrapper(
        F('data_fim_autorizacao') - today, 
        output_field=fields.DurationField()
    )

    queryset = queryset.annotate(
        dias_restantes=dias_timedelta
    )

    exclusividade = query_params.get('exclusividade')
    validade_dias = query_params.get('validade_dias')
    
    if exclusividade in ['true', 'false']:
        queryset = queryset.filter(possui_exclusividade=(exclusividade == 'true'))

    if validade_dias and validade_dias.isdigit():
        dias = int(validade_dias)
        
        if dias > 0:
            data_limite = today + timedelta(days=dias)
            queryset = queryset.filter(data_fim_autorizacao__lte=data_limite, data_fim_autorizacao__gte=today)
        elif dias == 0:
             queryset = queryset.filter(data_fim_autorizacao__lt=today)
    else:
        queryset = queryset.filter(data_fim_autorizacao__gte=today)

    queryset = queryset.order_by('data_fim_autorizacao')

    data_list = []
    for imovel in queryset:
        dias_restantes = imovel.dias_restantes.days
        
        status_risco = 'Ativo'
        if dias_restantes < 0:
             status_risco = 'Expirado'
        elif dias_restantes <= 30:
             status_risco = 'Risco (30 dias)'
        elif dias_restantes <= 90:
             status_risco = 'Atenção (90 dias)'

        data_list.append({
            'id': imovel.id,
            'codigo_referencia': imovel.codigo_referencia,
            'titulo_anuncio': imovel.titulo_anuncio,
            'proprietario': imovel.proprietario.nome if imovel.proprietario else 'N/A',
            'data_captacao': imovel.data_captacao,
            'data_fim_autorizacao': imovel.data_fim_autorizacao,
            'dias_restantes': dias_restantes,
            'status_risco': status_risco,
            'exclusividade': "Sim" if imovel.possui_exclusividade else "Não",
            'comissao': imovel.comissao_percentual,
            'valor_venda': imovel.valor_venda or imovel.valor_aluguel,
        })
    return data_list


class AutorizacaoReportView(APIView):
    permission_classes = [permissions.IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        data = _get_autorizacao_queryset(request.query_params)
        return Response(data, status=status.HTTP_200_OK)


class AutorizacaoReportPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = _get_autorizacao_queryset(request.query_params)
        
        validade_dias_param = request.query_params.get('validade_dias')
        exclusividade_param = request.query_params.get('exclusividade')
        
        titulo_relatorio = "Relatório de Autorizações"
        if validade_dias_param == '0':
            titulo_relatorio = "Relatório de Autorizações Expiradas"
        elif validade_dias_param:
            titulo_relatorio = f"Relatório de Autorizações Vencendo em {validade_dias_param} Dias"
        else:
            titulo_relatorio = "Relatório de Autorizações Ativas"
            
        if exclusividade_param == 'true':
            titulo_relatorio += " (Apenas Exclusivos)"
        elif exclusividade_param == 'false':
             titulo_relatorio += " (Apenas Não Exclusivos)"

        context = {
            'data': data,
            'titulo_relatorio': titulo_relatorio,
            'data_geracao': date.today(),
            'imobiliaria': request.tenant, 
        }

        html_string = render_to_string('relatorio_autorizacoes_template.html', context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result, encoding='UTF-8')

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f'relatorio_autorizacoes_{date.today().isoformat()}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            print(f"Erro ao gerar PDF do relatório: {pdf.err}")
            return HttpResponse(f"Erro ao gerar o PDF: {pdf.err}", status=500)
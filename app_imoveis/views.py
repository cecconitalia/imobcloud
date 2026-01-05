# C:\wamp64\www\ImobCloud\app_imoveis\views.py

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework import filters
from django.core.mail import send_mail
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.db import models, transaction
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, QueryDict, Http404 
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Count, Q, Case, When, Value, CharField, Max, F, ExpressionWrapper, fields, Sum 
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
    ImovelSimplificadoSerializer 
)
from core.models import Imobiliaria, PerfilUsuario, Notificacao
from app_clientes.models import Cliente, Oportunidade 
from app_config_ia.models import ModeloDePrompt
from core.serializers import ImobiliariaPublicSerializer

# ===================================================================
# VIEWS PÚBLICAS
# ===================================================================

class ImovelPublicListView(ListAPIView):
    serializer_class = ImovelPublicSerializer
    permission_classes = [permissions.AllowAny]
    # Mantém a correção da paginação para o site
    pagination_class = None

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

        if self.request.user.is_authenticated and getattr(self.request, 'tenant', None):
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
        if getattr(self.request, 'tenant', None):
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
            api_key = getattr(imobiliaria_obj, 'google_api_key', None) 
            if not api_key:
                api_key = os.getenv("GOOGLE_API_KEY")

            if not api_key:
                return Response(
                    {"error": "Chave de API não encontrada."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            genai.configure(api_key=api_key)
            
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
            mensagem_vaga = search_params.get('mensagem_resposta', "Não consegui identificar parâmetros de busca válidos.")
            return Response({
                 "mensagem": mensagem_vaga,
                 "imoveis": []
            }, status=status.HTTP_200_OK)
        
        status_filtro_ia = search_params.get('status')
        if status_filtro_ia and status_filtro_ia in Imovel.Status.values:
             base_queryset = base_queryset.filter(status=status_filtro_ia)

        finalidade_param = search_params.get('finalidade')
        if finalidade_param and finalidade_param in Imovel.Finalidade.values:
            base_queryset = base_queryset.filter(finalidade=finalidade_param)

        tipo_param = search_params.get('tipo')
        if tipo_param:
            tipo_param = tipo_param.upper()
            if hasattr(Imovel.TipoImovel, tipo_param):
                base_queryset = base_queryset.filter(tipo=tipo_param)

        cidade_param = search_params.get('cidade')
        if cidade_param and isinstance(cidade_param, str):
            base_queryset = base_queryset.filter(cidade__icontains=cidade_param)

        bairro_param = search_params.get('bairro')
        if bairro_param and isinstance(bairro_param, str):
            base_queryset = base_queryset.filter(bairro__icontains=bairro_param)

        if 'valor_min' in search_params and search_params['valor_min'] is not None:
            try:
                valor_min_decimal = Decimal(str(search_params['valor_min']))
                q_filter_min = Q(valor_venda__gte=valor_min_decimal) if status_filtro_ia == Imovel.Status.A_VENDA else Q(valor_aluguel__gte=valor_min_decimal)
                if not status_filtro_ia: 
                    q_filter_min = Q(valor_venda__gte=valor_min_decimal) | Q(valor_aluguel__gte=valor_min_decimal)
                base_queryset = base_queryset.filter(q_filter_min)
            except (ValueError, TypeError, InvalidOperation):
                 pass 

        if 'valor_max' in search_params and search_params['valor_max'] is not None:
            try:
                 valor_max_decimal = Decimal(str(search_params['valor_max']))
                 q_filter_max = Q(valor_venda__lte=valor_max_decimal) if status_filtro_ia == Imovel.Status.A_VENDA else Q(valor_aluguel__lte=valor_max_decimal)
                 if not status_filtro_ia:
                      q_filter_max = Q(valor_venda__lte=valor_max_decimal) | Q(valor_aluguel__lte=valor_max_decimal)
                 base_queryset = base_queryset.filter(q_filter_max)
            except (ValueError, TypeError, InvalidOperation):
                 pass 

        def apply_int_filter(param_name, field_name):
            val = search_params.get(param_name)
            if val is not None:
                try:
                    val_int = int(val)
                    if val_int >= 0:
                        kwargs = {f"{field_name}__gte": val_int}
                        return Q(**kwargs)
                except (ValueError, TypeError):
                    pass
            return None

        q_quartos = apply_int_filter('quartos_min', 'quartos')
        if q_quartos: base_queryset = base_queryset.filter(q_quartos)

        q_vagas = apply_int_filter('vagas_min', 'vagas_garagem')
        if q_vagas: base_queryset = base_queryset.filter(q_vagas)
        
        q_banheiros = apply_int_filter('banheiros_min', 'banheiros')
        if q_banheiros: base_queryset = base_queryset.filter(q_banheiros)
        
        q_suites = apply_int_filter('suites_min', 'suites')
        if q_suites: base_queryset = base_queryset.filter(q_suites)

        q_andar = apply_int_filter('andar_min', 'andar')
        if q_andar: base_queryset = base_queryset.filter(q_andar)

        area_min_ia = search_params.get('area_min')
        if area_min_ia is not None:
            try:
                 area_val = Decimal(str(area_min_ia))
                 if area_val > 0:
                      base_queryset = base_queryset.filter(
                           Q(area_util__gte=area_val) | 
                           Q(area_construida__gte=area_val)
                      )
            except (ValueError, TypeError, InvalidOperation):
                 pass

        features_map = {
            'aceita_pet': 'aceita_pet',
            'mobiliado': 'mobiliado',
            'piscina': None,
            'ar_condicionado': 'ar_condicionado',
            'salao_festas': 'salao_festas',
            'elevador': 'elevador'
        }

        for json_key, model_field in features_map.items():
            if search_params.get(json_key) is True:
                if json_key == 'piscina':
                    base_queryset = base_queryset.filter(Q(piscina_privativa=True) | Q(piscina_condominio=True))
                elif model_field:
                    base_queryset = base_queryset.filter(**{model_field: True})

        serializer = ImovelPublicSerializer(base_queryset, many=True)
        mensagem_resposta = search_params.get('mensagem_resposta', "Resultados da sua pesquisa com IA.")
        if not base_queryset.exists():
            mensagem_resposta = "Não encontrei nenhum imóvel que corresponda exatamente à sua procura. Tente simplificar a pesquisa."

        return Response({
            "mensagem": mensagem_resposta,
            "imoveis": serializer.data
        }, status=status.HTTP_200_OK)


# ===================================================================
# VIEWS INTERNAS
# ===================================================================

class ImovelViewSet(viewsets.ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    
    lookup_value_regex = r'\d+' 

    search_fields = [
        'logradouro', 'cidade', 'titulo_anuncio', 'codigo_referencia', 'bairro',
        'proprietario__nome', 'proprietario__razao_social', 'proprietario__documento'
    ] 

    def get_queryset(self):
        user = self.request.user
        
        # Lógica de fallback para Tenant
        tenant = getattr(self.request, 'tenant', None)
        if not tenant and hasattr(user, 'imobiliaria'):
            tenant = user.imobiliaria

        print(f"DEBUG IMOVEL: User={user}, Superuser={user.is_superuser}, Tenant={tenant}")

        if user.is_superuser:
            if not tenant:
                 base_queryset = Imovel.objects.all()
            else:
                 base_queryset = Imovel.objects.filter(imobiliaria=tenant)
        elif tenant:
            base_queryset = Imovel.objects.filter(imobiliaria=tenant)
        else:
            return Imovel.objects.none()

        status_param = self.request.query_params.get('status', None)
        if status_param:
             if status_param in Imovel.Status.values:
                base_queryset = base_queryset.filter(status=status_param)
        elif self.action in ['list', 'lista_simples']: 
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
        print(f"DEBUG IMOVEL CREATE: Iniciando cadastro para usuário {self.request.user}")
        
        tenant = getattr(self.request, 'tenant', None)
        if not tenant and hasattr(self.request.user, 'imobiliaria'):
            tenant = self.request.user.imobiliaria
            
        if self.request.user.is_superuser:
            if 'imobiliaria' in self.request.data:
                imobiliaria_id = self.request.data['imobiliaria']
                imobiliaria_obj = get_object_or_404(Imobiliaria, pk=imobiliaria_id)
                serializer.save(imobiliaria=imobiliaria_obj)
                print("DEBUG IMOVEL CREATE: Salvo com imobiliária do formulário.")
                return

            if tenant:
                serializer.save(imobiliaria=tenant)
                print("DEBUG IMOVEL CREATE: Salvo com tenant detectado.")
                return

            first_tenant = Imobiliaria.objects.first()
            if first_tenant:
                serializer.save(imobiliaria=first_tenant)
                print(f"DEBUG IMOVEL CREATE: Fallback para primeira imobiliária: {first_tenant}")
                return
            else:
                raise PermissionDenied("Nenhuma imobiliária cadastrada no sistema.")

        elif tenant:
            serializer.save(imobiliaria=tenant)
            print("DEBUG IMOVEL CREATE: Imóvel salvo com sucesso (usuário comum).")
        else:
            print("DEBUG IMOVEL CREATE: ERRO - Tenant não identificado.")
            raise PermissionDenied("Não foi possível associar o imóvel a uma imobiliária. Tenant não identificado.")

    def perform_update(self, serializer):
        instance = serializer.instance
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)
        
        if self.request.user.is_superuser or (tenant and instance.imobiliaria == tenant):
             serializer.save()
        else:
             raise PermissionDenied("Você não tem permissão para atualizar este imóvel.")

    def perform_destroy(self, instance):
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)
        
        if self.request.user.is_superuser or (tenant and instance.imobiliaria == tenant):
             instance.status = Imovel.Status.DESATIVADO
             instance.publicado_no_site = False
             instance.save()
             return Response(status=status.HTTP_200_OK)
        else:
             raise PermissionDenied("Você não tem permissão para inativar este imóvel.")

    @action(detail=False, methods=['get'], url_path='lista-simples')
    def lista_simples(self, request):
        queryset = self.get_queryset()
        serializer = ImovelSimplificadoSerializer(queryset, many=True)
        return Response(serializer.data)

    def _get_imovel_contexto_para_ia(self, imovel):
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
            # Tenta pegar a chave do campo 'google_api_key' da imobiliária do imóvel
            # Se o nome do campo for diferente no seu modelo, ajuste 'google_api_key' aqui
            api_key = getattr(imovel.imobiliaria, 'google_api_key', None)

            if not api_key:
                # Fallback: Tenta pegar das variáveis de ambiente
                api_key = os.getenv("GOOGLE_API_KEY")

            if not api_key:
                return Response(
                    {"error": "Chave de API da Google não configurada na imobiliária deste imóvel. Cadastre-a no Admin."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            genai.configure(api_key=api_key)

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
        user = self.request.user
        tenant = getattr(self.request, 'tenant', None) or getattr(user, 'imobiliaria', None)
        
        if user.is_superuser:
            if not tenant:
                return ImagemImovel.objects.all()
            return ImagemImovel.objects.filter(imovel__imobiliaria=tenant)
            
        if tenant:
            return ImagemImovel.objects.filter(imovel__imobiliaria=tenant)
        return ImagemImovel.objects.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        imovel_id = request.data.get('imovel')
        if not imovel_id:
            return Response({'imovel': ['O ID do imóvel é obrigatório.']}, status=status.HTTP_400_BAD_REQUEST)

        tenant = getattr(self.request, 'tenant', None) or getattr(request.user, 'imobiliaria', None)

        try:
            if request.user.is_superuser:
                 if tenant:
                     imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=tenant)
                 else:
                     imovel = Imovel.objects.get(pk=imovel_id)
            elif tenant:
                 imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=tenant)
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
        tenant = getattr(self.request, 'tenant', None) or getattr(self.request.user, 'imobiliaria', None)
        
        if not (self.request.user.is_superuser or (tenant and instance.imovel.imobiliaria == tenant)):
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

        tenant = getattr(self.request, 'tenant', None) or getattr(request.user, 'imobiliaria', None)

        try:
            if request.user.is_superuser:
                 if tenant:
                     imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=tenant)
                 else:
                     imovel = Imovel.objects.get(pk=imovel_id)
            elif tenant:
                 imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=tenant)
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
        
        user = self.request.user
        tenant = getattr(self.request, 'tenant', None) or getattr(user, 'imobiliaria', None)
        
        if user.is_superuser:
            if not tenant:
                return base_queryset.all().order_by('-data_contato')
            return base_queryset.filter(imovel__imobiliaria=tenant).order_by('-data_contato')
        elif user.is_authenticated and tenant:
            return base_queryset.filter(imovel__imobiliaria=tenant).order_by('-data_contato')
        return ContatoImovel.objects.none()

    @transaction.atomic 
    def perform_create(self, serializer):
        # VALIDAÇÃO MANUAL DO TELEFONE
        # Garante que o telefone venha preenchido, caso contrário bloqueia (Erro 400)
        dados = serializer.validated_data
        if not dados.get('telefone'):
             raise ValidationError({"telefone": ["Este campo é obrigatório para o contato."]})

        contato = serializer.save()
        imovel = contato.imovel
        imobiliaria = imovel.imobiliaria
        
        cliente_para_oportunidade = None
        oportunidade = None

        # 1. Tentar encontrar ou criar o Cliente (Lead Provisório)
        cliente_por_email = Cliente.objects.filter(imobiliaria=imobiliaria, email__iexact=contato.email).first()

        if cliente_por_email:
            cliente_para_oportunidade = cliente_por_email
            
        else:
            # Cliente novo: cria o registro
            documento_provisorio = f"99999{contato.id:06d}"[:11].ljust(11, '0') 

            try:
                novo_cliente = Cliente.objects.create(
                    imobiliaria=imobiliaria,
                    tipo_pessoa='FISICA', 
                    documento=documento_provisorio, 
                    nome=contato.nome,
                    email=contato.email,
                    telefone=contato.telefone,
                    preferencias_imovel=f"Interesse pelo imóvel #{imovel.codigo_referencia or imovel.id}. Mensagem: {contato.mensagem}",
                    perfil_cliente=['Interessado', 'Lead'],
                    ativo=True
                )
                cliente_para_oportunidade = novo_cliente
            except Exception as e:
                print(f"ERRO CRÍTICO AO CRIAR CLIENTE PARA O LEAD: {e}")
                cliente_para_oportunidade = None 

        
        # 2. Criar a Oportunidade
        if cliente_para_oportunidade:
             oportunidade_existente = Oportunidade.objects.filter(
                 imobiliaria=imobiliaria,
                 imovel=imovel,
                 cliente=cliente_para_oportunidade
             ).exclude(fase__in=[Oportunidade.Fases.GANHO, Oportunidade.Fases.PERDIDO]).first()
             
             if not oportunidade_existente:
                 oportunidade = Oportunidade.objects.create(
                     imobiliaria=imobiliaria,
                     imovel=imovel,
                     cliente=cliente_para_oportunidade,
                     fase=Oportunidade.Fases.LEAD,
                     fonte=Oportunidade.Fontes.SITE,
                     titulo=f"Lead Site: {imovel.titulo_anuncio or imovel.tipo} ({contato.nome})",
                     valor_estimado=imovel.valor_venda or imovel.valor_aluguel,
                     informacoes_adicionais=f"Mensagem do Lead: {contato.mensagem}"
                 )
                 
                 # 3. Notificação no Painel
                 responsavel = oportunidade.responsavel
                 if not responsavel:
                     # CORREÇÃO CRÍTICA: Removido .select_related('user') pois causava FieldError.
                     # Também usamos getattr(admin_perfil, 'user', admin_perfil) para suportar
                     # tanto se PerfilUsuario for um modelo de perfil (com user) ou o próprio usuário.
                     admin_perfil = PerfilUsuario.objects.filter(
                         imobiliaria=imobiliaria, 
                         is_admin=True
                     ).first()
                     
                     if admin_perfil:
                         responsavel = getattr(admin_perfil, 'user', admin_perfil)
                     else:
                          responsavel = None 

                 if responsavel:
                     Notificacao.objects.create(
                         destinatario=responsavel,
                         mensagem=f"Novo Lead do Site! Cliente: {contato.nome}. Oportunidade criada: {oportunidade.titulo}.",
                         link=f"/funil-vendas?id={oportunidade.id}" 
                     )
             else:
                 oportunidade = oportunidade_existente
            
             self.created_oportunidade_id = oportunidade.id
             self.created_cliente_id = cliente_para_oportunidade.id 
                 
        try:
            if hasattr(imobiliaria, 'email_contato') and imobiliaria.email_contato:
                destinatario_email = imobiliaria.email_contato
                assunto = f"Novo Contato para o Imóvel: {contato.imovel.titulo_anuncio or contato.imovel.logradouro}"
                base_url_painel = "http://localhost:5173" # Ou a URL de produção
                link_imovel_painel = f"{base_url_painel}/imoveis/editar/{contato.imovel.id}"

                mensagem_corpo = f"""
                Você recebeu um novo contato através do site!
                Nome: {contato.nome}
                Email: {contato.email}
                Telefone: {contato.telefone}
                Imóvel: {contato.imovel.titulo_anuncio} ({contato.imovel.codigo_referencia})
                Mensagem: {contato.mensagem}
                
                """
                if oportunidade:
                    mensagem_corpo += f"Uma oportunidade (ID: {oportunidade.id}) foi criada automaticamente no funil. "
                    mensagem_corpo += f"Link para a Oportunidade: {base_url_painel}/oportunidades/editar/{oportunidade.id}\n"
                
                mensagem_corpo += f"Acesse o painel para ver os detalhes do Imóvel: {link_imovel_painel}"
                
                remetente = settings.DEFAULT_FROM_EMAIL
                send_mail(assunto, mensagem_corpo, remetente, [destinatario_email], fail_silently=False)

        except Exception as e:
            print(f"ERRO AO ENVIAR NOTIFICAÇÕES DE CONTATO: {e}")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        oportunidade_id = getattr(self, 'created_oportunidade_id', None)
        cliente_id = getattr(self, 'created_cliente_id', None)

        if oportunidade_id:
             return Response({
                 'status': 'success',
                 'message': 'Lead, Cliente e Oportunidade criados com sucesso.',
                 'oportunidade_id': oportunidade_id,
                 'cliente_id': cliente_id, 
                 'redirect_url': f'/oportunidades/editar/{oportunidade_id}?cliente_id={cliente_id}' 
             }, status=status.HTTP_201_CREATED)
        else:
             headers = self.get_success_headers(serializer.data)
             return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def arquivar(self, request, pk=None):
        contato = self.get_object()
        contato.arquivado = True
        contato.save()
        return Response({'status': 'Contacto arquivado com sucesso'}, status=status.HTTP_200_OK)


class GerarAutorizacaoPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_imovel_data(self, request, imovel_id):
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'imobiliaria', None)

        try:
            if request.user.is_superuser:
                 if tenant:
                     imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=tenant)
                 else:
                     imovel = Imovel.objects.get(pk=imovel_id)
            elif tenant:
                 imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=tenant)
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
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'imobiliaria', None)
        
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

def _get_autorizacao_queryset(tenant, query_params): 
    """
    Helper para relatório completo em Paisagem.
    """
    queryset = Imovel.objects.filter(
        imobiliaria=tenant
    ).exclude(status=Imovel.Status.DESATIVADO).select_related('proprietario')
    
    today = date.today()
    trinta_dias = today + timedelta(days=30)
    
    # --- FILTROS (Mantidos iguais) ---
    search = query_params.get('search')
    if search:
        queryset = queryset.filter(
            Q(codigo_referencia__icontains=search) |
            Q(titulo_anuncio__icontains=search) |
            Q(logradouro__icontains=search) |
            Q(bairro__icontains=search) |
            Q(proprietario__nome__icontains=search) |
            Q(proprietario__razao_social__icontains=search)
        )

    tipo_negocio = query_params.get('tipo_negocio')
    if tipo_negocio:
        queryset = queryset.filter(status=tipo_negocio)

    vencimento_de = query_params.get('vencimento_de')
    vencimento_ate = query_params.get('vencimento_ate')
    if vencimento_de:
        queryset = queryset.filter(data_fim_autorizacao__gte=vencimento_de)
    if vencimento_ate:
        queryset = queryset.filter(data_fim_autorizacao__lte=vencimento_ate)

    status_vigencia = query_params.get('status_vigencia')
    if status_vigencia:
        if status_vigencia == 'VIGENTE':
            queryset = queryset.filter(Q(data_fim_autorizacao__gte=today) | Q(data_fim_autorizacao__isnull=True))
        elif status_vigencia == 'VENCIDA':
            queryset = queryset.filter(data_fim_autorizacao__lt=today)
        elif status_vigencia == 'A_VENCER':
            queryset = queryset.filter(data_fim_autorizacao__gte=today, data_fim_autorizacao__lte=trinta_dias)

    # Ordenação e Anotação
    dias_timedelta = ExpressionWrapper(F('data_fim_autorizacao') - today, output_field=fields.DurationField())
    queryset = queryset.annotate(dias_restantes=dias_timedelta).order_by('data_fim_autorizacao')

    # --- PROCESSAMENTO DOS DADOS COMPLETOS ---
    data_list = []
    total_imoveis = 0
    total_expirados = 0
    total_venda_potencial = Decimal(0)
    total_aluguel_potencial = Decimal(0)

    for imovel in queryset:
        # Dias Restantes
        if imovel.data_fim_autorizacao and imovel.dias_restantes:
             dias_restantes = imovel.dias_restantes.days
        else:
             dias_restantes = 9999 
        
        # Status Risco
        status_risco = 'Ativo'
        if imovel.data_fim_autorizacao and dias_restantes < 0:
             status_risco = 'Expirado'
             total_expirados += 1
        elif imovel.data_fim_autorizacao and dias_restantes <= 30:
             status_risco = 'Risco (30 dias)'
        
        total_imoveis += 1
        
        # Somatórios separados
        if imovel.valor_venda: total_venda_potencial += imovel.valor_venda
        if imovel.valor_aluguel: total_aluguel_potencial += imovel.valor_aluguel
        
        # Formatações de Valor
        def fmt_money(val):
            return f"{val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if val else "-"

        # Dados do Proprietário
        nome_proprietario = 'N/A'
        telefone_proprietario = '-'
        email_proprietario = '-'
        
        if imovel.proprietario:
            p = imovel.proprietario
            nome_proprietario = p.razao_social if p.tipo_pessoa == 'JURIDICA' and p.razao_social else p.nome
            telefone_proprietario = p.telefone or p.celular or '-'
            email_proprietario = p.email or '-'

        # Status Display
        finalidade_display = "Venda" if imovel.status == Imovel.Status.A_VENDA else "Aluguel"
        if imovel.status not in [Imovel.Status.A_VENDA, Imovel.Status.PARA_ALUGAR]:
             finalidade_display = imovel.get_status_display()

        data_list.append({
            'id': imovel.id, # CORREÇÃO: Adicionado ID para o frontend
            'codigo': imovel.codigo_referencia,
            'titulo': imovel.titulo_anuncio,
            'endereco_resumido': f"{imovel.logradouro or ''}, {imovel.numero or ''}",
            'bairro_cidade': f"{imovel.bairro or ''} - {imovel.cidade or ''}",
            
            'proprietario_nome': nome_proprietario,
            'proprietario_tel': telefone_proprietario,
            'proprietario_email': email_proprietario,
            
            'finalidade': finalidade_display,
            'exclusividade': "SIM" if imovel.possui_exclusividade else "NÃO",
            'comissao': f"{imovel.comissao_percentual}%" if imovel.comissao_percentual else "-",
            
            'valor_venda': fmt_money(imovel.valor_venda),
            'valor_aluguel': fmt_money(imovel.valor_aluguel),
            
            'data_inicio': imovel.data_captacao,
            'data_fim': imovel.data_fim_autorizacao,
            'dias_restantes': dias_restantes,
            'status_risco': status_risco,
        })
        
    def fmt_total(val):
        return f"R$ {val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    sumario_data = {
        'total_imoveis': total_imoveis,
        'total_expirados': total_expirados,
        'total_venda': fmt_total(total_venda_potencial),
        'total_aluguel': fmt_total(total_aluguel_potencial)
    }
    
    return {'list': data_list, 'summary': sumario_data}

class AutorizacaoReportView(APIView):
    permission_classes = [permissions.IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'imobiliaria', None)
        
        if not tenant and request.user.is_superuser:
            tenant = Imobiliaria.objects.first()
        if not tenant: return Response({"error": "Tenant não identificado."}, status=400)

        data = _get_autorizacao_queryset(tenant, request.query_params) 
        return Response(data['list'], status=status.HTTP_200_OK) 


class AutorizacaoReportPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 1. Definição do Tenant (Imobiliária)
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'imobiliaria', None)
        
        if not tenant and request.user.is_superuser:
            tenant = Imobiliaria.objects.first()
        
        if not tenant:
            return HttpResponse("Erro: Nenhuma imobiliária identificada.", status=400)

        # 2. Busca de Dados (Usando o helper criado anteriormente)
        # O helper processa todos os filtros: data, texto, tipo e status
        data_structure = _get_autorizacao_queryset(tenant, request.query_params) 
        data = data_structure['list']
        summary = data_structure['summary']
        
        # 3. Personalização do Título do Relatório (baseado nos filtros)
        titulo_relatorio = "Relatório de Autorizações"
        
        status_vigencia = request.query_params.get('status_vigencia')
        tipo_negocio = request.query_params.get('tipo_negocio')
        
        # Adiciona sufixo ao título se houver filtros específicos
        if status_vigencia == 'VIGENTE':
            titulo_relatorio += " (Vigentes)"
        elif status_vigencia == 'VENCIDA':
            titulo_relatorio += " (Vencidas)"
        elif status_vigencia == 'A_VENCER':
            titulo_relatorio += " (A Vencer)"
            
        if tipo_negocio == 'A_VENDA':
            titulo_relatorio += " - Venda"
        elif tipo_negocio == 'PARA_ALUGAR':
            titulo_relatorio += " - Aluguel"

        # 4. Contexto para o Template
        context = {
            'data': data,
            'summary': summary,
            'titulo_relatorio': titulo_relatorio,
            # CORREÇÃO: Usa timezone.now() para passar data E hora, permitindo formatação H:i no template
            'data_geracao': timezone.now(), 
            'imobiliaria': tenant,
            'usuario_solicitante': request.user.first_name or request.user.username
        }

        # 5. Renderização do HTML
        # O Django buscará este arquivo em: app_imoveis/templates/relatorio_autorizacoes_template.html
        html_string = render_to_string('relatorio_autorizacoes_template.html', context)
        
        # 6. Geração do PDF (xhtml2pdf)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result, encoding='UTF-8')

        # 7. Retorno do Arquivo
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            # Usa timezone.now() também para o nome do arquivo
            filename = f'relatorio_autorizacoes_{timezone.now().strftime("%Y-%m-%d")}.pdf'
            
            # 'inline' abre no navegador (nova aba) para visualização antes de imprimir
            response['Content-Disposition'] = f'inline; filename="{filename}"' 
            return response
        else:
            return HttpResponse(f"Erro ao gerar o PDF: {pdf.err}", status=500)
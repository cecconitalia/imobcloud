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
from django.http import HttpResponse, QueryDict, Http404 # ADICIONADO Http404
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Count, Q, Case, When, Value, CharField, Max
from io import BytesIO
from xhtml2pdf import pisa
import locale
from num2words import num2words
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
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
    # Garanta que sua GOOGLE_API_KEY está configurada nas variáveis de ambiente (.env)
    api_key=os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("AVISO: GOOGLE_API_KEY não encontrada nas variáveis de ambiente.")
    else:
        genai.configure(api_key=api_key)
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
        # Removendo prints de depuração que não são mais necessários
        subdomain_param = self.request.query_params.get('subdomain', None)

        # 1. Extração dos parâmetros de filtro (mantidos)
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

        # --- INÍCIO DA LÓGICA DE IDENTIFICAÇÃO DO TENANT ---
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

        # 2. BASE QUERYSET FILTRADO PELO TENANT ENCONTRADO
        base_queryset = Imovel.objects.filter(imobiliaria=imobiliaria_obj)

        # 3. FILTRO DE VISIBILIDADE (SE NÃO AUTENTICADO, MOSTRA APENAS PUBLICADOS E NÃO DESATIVADOS)
        if not self.request.user.is_authenticated:
            base_queryset = base_queryset.filter(publicado_no_site=True)
            if not status_param:
                base_queryset = base_queryset.exclude(status='DESATIVADO')
        else:
             if not status_param:
                 base_queryset = base_queryset.exclude(status='DESATIVADO')
             else:
                 base_queryset = base_queryset.filter(status=status_param)

        # 4. APLICAÇÃO DOS FILTROS DINÂMICOS RESTANTES (finalidade, tipo, cidade, etc.)
        if finalidade: base_queryset = base_queryset.filter(finalidade=finalidade)
        if tipo: base_queryset = base_queryset.filter(tipo=tipo)
        if cidade: base_queryset = base_queryset.filter(cidade__icontains=cidade)
        if valor_min:
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
        if status_param:
             base_queryset = base_queryset.filter(status=status_param)

        return base_queryset


class ImovelPublicDetailView(RetrieveAPIView):
    """
    View para detalhar um imóvel específico no site público.
    """
    serializer_class = ImovelPublicSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Imovel.objects.filter(publicado_no_site=True) # Filtro base
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


# --- NOVO ENDPOINT DE BUSCA COM IA ---
class ImovelIAView(APIView):
    """
    Endpoint de busca pública que utiliza IA para interpretar o texto do utilizador.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        print("\n--- ImovelIAView ---") # DEBUG
        user_query = request.data.get('query')
        print(f"Query Recebida: {user_query}") # DEBUG
        subdomain_param = request.query_params.get('subdomain', None)
        print(f"Subdomain Parâmetro (IA): {subdomain_param}") # DEBUG

        if not user_query:
            return Response({"error": "O campo 'query' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        # Identifica a imobiliária ANTES de chamar a IA
        imobiliaria_obj = None
        if subdomain_param:
            try:
                imobiliaria_obj = Imobiliaria.objects.get(subdominio__iexact=subdomain_param)
                print(f"Tenant (IA) encontrado via subdomain param: {imobiliaria_obj}") # DEBUG
            except Imobiliaria.DoesNotExist:
                 print(f"Imobiliária (IA) com subdomínio '{subdomain_param}' NÃO encontrada.") # DEBUG
                 return Response({
                    "mensagem": "Imobiliária não encontrada.",
                    "imoveis": []
                 }, status=status.HTTP_404_NOT_FOUND)
        else:
             print("Subdomínio não fornecido para busca IA.") # DEBUG
             return Response({
                    "mensagem": "Subdomínio da imobiliária não fornecido.",
                    "imoveis": []
                 }, status=status.HTTP_400_BAD_REQUEST)

        # 1. Obter o prompt da base de dados
        try:
            prompt_config = ModeloDePrompt.objects.get(em_uso_busca=True)
            template_prompt = prompt_config.template_do_prompt
        except ModeloDePrompt.DoesNotExist:
            return Response(
                {"error": "Nenhum modelo de prompt para busca por IA está ativo."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        prompt_final = template_prompt.replace('{{user_query}}', user_query)
        print(f"Prompt final enviado para IA: {prompt_final}") # DEBUG

        # 2. Enviar para a API da IA para traduzir o texto em JSON
        try:
            model_name = 'models/gemini-flash-latest' # Usando o modelo que funcionou
            model = genai.GenerativeModel(model_name)
            print(f"Usando modelo Gemini: '{model_name}'") # DEBUG

            response = model.generate_content(prompt_final)

            if not response.parts:
                 print("DEBUG: Resposta da IA não contém 'parts'.")
                 raise ValueError("Resposta inesperada da IA.")

            json_text_raw = response.parts[0].text
            print(f"Texto bruto recebido da IA: ```{json_text_raw}```") # DEBUG

            json_text = json_text_raw.strip().lstrip('```json').rstrip('```').strip()
            search_params = json.loads(json_text)

            print(f"DEBUG DA IA: Parâmetros JSON decodificados: {search_params}") # DEBUG

        except json.JSONDecodeError as json_err:
             print(f"DEBUG: Erro ao decodificar JSON da resposta da IA: {json_err}")
             print(f"DEBUG: Texto (após limpeza) que falhou: {json_text}")
             return Response(
                 {"error": f"A IA retornou uma resposta em formato inválido. Tente novamente."},
                 status=status.HTTP_503_SERVICE_UNAVAILABLE
             )
        except Exception as e:
            print(f"DEBUG: Erro na API do Google Gemini durante a busca: {e}")
            if "is not found" in str(e) or "is not supported" in str(e):
                 error_message = f"O modelo de IA '{model_name}' não está disponível. Tente outro modelo ou verifique sua API Key. ({e})"
            else:
                 error_message = f"Não consegui interpretar a sua pesquisa. Tente ser mais específico. ({e})"
            return Response({"error": error_message}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


        # 3. Usar os parâmetros da IA para filtrar os imóveis
        base_queryset = Imovel.objects.filter(
            imobiliaria=imobiliaria_obj,
            publicado_no_site=True
        ).exclude(status=Imovel.Status.DESATIVADO)
        print(f"Contagem inicial (IA) para {imobiliaria_obj}: {base_queryset.count()}") # DEBUG

        # --- Verificação de Busca Válida ---
        if search_params.get('busca_valida') == False:
            mensagem_vaga = search_params.get('mensagem_resposta', "Não consegui identificar parâmetros de busca válidos. Por favor, especifique o que você procura.")
            return Response({
                    "mensagem": mensagem_vaga,
                    "imoveis": []
                 }, status=status.HTTP_200_OK)


        # Aplica os filtros extraídos da IA
        if 'finalidade' in search_params:
            finalidade_param = search_params['finalidade']
            if finalidade_param in Imovel.Finalidade.values:
                base_queryset = base_queryset.filter(finalidade=finalidade_param)

        if 'tipo' in search_params:
            tipo_param = search_params['tipo'].upper()
            if hasattr(Imovel.TipoImovel, tipo_param):
                base_queryset = base_queryset.filter(tipo=tipo_param)
            else:
                 print(f"Aviso IA: Tipo de imóvel '{tipo_param}' não reconhecido.")

        if 'cidade' in search_params:
            base_queryset = base_queryset.filter(cidade__icontains=search_params['cidade'])

        if 'bairro' in search_params:
            bairro_param = search_params['bairro']
            if bairro_param and isinstance(bairro_param, str): # Garante que é uma string não vazia
                # Usamos icontains para busca case-insensitive e parcial
                base_queryset = base_queryset.filter(bairro__icontains=bairro_param)
                print(f"Aplicado filtro bairro__icontains='{bairro_param}'") # DEBUG
            else:
                 print(f"Aviso IA: 'bairro' inválido ou vazio: {bairro_param}")


        finalidade_filtro_ia = search_params.get('finalidade', None)
        if 'valor_min' in search_params:
            valor_min_ia = search_params['valor_min']
            # Validação mais robusta para valor_min
            try:
                valor_min_decimal = Decimal(valor_min_ia)
                q_filter_min = Q(valor_venda__gte=valor_min_decimal) if finalidade_filtro_ia == Imovel.Status.A_VENDA else Q(valor_aluguel__gte=valor_min_decimal)
                if not finalidade_filtro_ia:
                     q_filter_min = Q(valor_venda__gte=valor_min_decimal) | Q(valor_aluguel__gte=valor_min_decimal)
                base_queryset = base_queryset.filter(q_filter_min)
            except (ValueError, TypeError, InvalidOperation): # InvalidOperation para Decimal
                 print(f"Aviso IA: 'valor_min' inválido: {valor_min_ia}")


        if 'valor_max' in search_params:
            valor_max_ia = search_params['valor_max']
             # Validação mais robusta para valor_max
            try:
                 valor_max_decimal = Decimal(valor_max_ia)
                 q_filter_max = Q(valor_venda__lte=valor_max_decimal) if finalidade_filtro_ia == Imovel.Finalidade.A_VENDA else Q(valor_aluguel__lte=valor_max_decimal)
                 if not finalidade_filtro_ia:
                      q_filter_max = Q(valor_venda__lte=valor_max_decimal) | Q(valor_aluguel__lte=valor_max_decimal)
                 base_queryset = base_queryset.filter(q_filter_max)
            except (ValueError, TypeError, InvalidOperation):
                 print(f"Aviso IA: 'valor_max' inválido: {valor_max_ia}")


        if 'quartos_min' in search_params:
            try:
                quartos_min_ia = int(search_params['quartos_min'])
                if quartos_min_ia >= 0: # Garante que não é negativo
                     base_queryset = base_queryset.filter(quartos__gte=quartos_min_ia)
            except (ValueError, TypeError):
                 print(f"Aviso IA: 'quartos_min' inválido: {search_params['quartos_min']}")

        if 'vagas_min' in search_params:
            try:
                 vagas_min_ia = int(search_params['vagas_min'])
                 if vagas_min_ia >= 0:
                      base_queryset = base_queryset.filter(vagas_garagem__gte=vagas_min_ia)
            except (ValueError, TypeError):
                 print(f"Aviso IA: 'vagas_min' inválido: {search_params['vagas_min']}")
        
        if 'banheiros_min' in search_params:
            try:
                 banheiros_min_ia = int(search_params['banheiros_min'])
                 if banheiros_min_ia >= 0:
                      # O campo no modelo é 'banheiros'
                      base_queryset = base_queryset.filter(banheiros__gte=banheiros_min_ia) 
                      print(f"Aplicado filtro banheiros__gte='{banheiros_min_ia}'") # DEBUG
            except (ValueError, TypeError):
                 print(f"Aviso IA: 'banheiros_min' inválido: {search_params.get('banheiros_min')}")

        
        # --- INÍCIO DA ATUALIZAÇÃO (NOVOS FILTROS) ---
        if 'suites_min' in search_params:
            try:
                suites_min_ia = int(search_params['suites_min'])
                if suites_min_ia >= 0:
                     base_queryset = base_queryset.filter(suites__gte=suites_min_ia) #
                     print(f"Aplicado filtro suites__gte='{suites_min_ia}'") # DEBUG
            except (ValueError, TypeError):
                 print(f"Aviso IA: 'suites_min' inválido.")

        if 'andar_min' in search_params:
            try:
                 andar_min_ia = int(search_params['andar_min'])
                 if andar_min_ia >= 0:
                      base_queryset = base_queryset.filter(andar__gte=andar_min_ia) #
                      print(f"Aplicado filtro andar__gte='{andar_min_ia}'") # DEBUG
            except (ValueError, TypeError):
                 print(f"Aviso IA: 'andar_min' inválido.")

        if 'area_min' in search_params:
            # Filtra pela area util OU construida
            try:
                area_min_ia = Decimal(search_params['area_min'])
                if area_min_ia > 0:
                     # Usa Q para filtrar em area_util OU area_construida
                     base_queryset = base_queryset.filter(
                         Q(area_util__gte=area_min_ia) | 
                         Q(area_construida__gte=area_min_ia)
                    )
                     print(f"Aplicado filtro area_min__gte='{area_min_ia}'") # DEBUG
            except (ValueError, TypeError, InvalidOperation):
                 print(f"Aviso IA: 'area_min' inválido.")
        # --- FIM DA ATUALIZAÇÃO ---


        if search_params.get('aceita_pet') == True:
            base_queryset = base_queryset.filter(aceita_pet=True) #
        if search_params.get('mobiliado') == True:
            base_queryset = base_queryset.filter(mobiliado=True) #
        if search_params.get('piscina') == True:
            # Mantido, busca por piscina privativa OU em condomínio
            base_queryset = base_queryset.filter(Q(piscina_privativa=True) | Q(piscina_condominio=True))
        
        # --- ATUALIZAÇÃO: FILTROS BOOLEANOS ADICIONAIS ---
        if search_params.get('ar_condicionado') == True:
             base_queryset = base_queryset.filter(ar_condicionado=True) #
        if search_params.get('salao_festas') == True:
             base_queryset = base_queryset.filter(salao_festas=True) #
        if search_params.get('elevador') == True:
             base_queryset = base_queryset.filter(elevador=True) #
        # --- FIM DA ATUALIZAÇÃO ---


        print(f"Contagem após filtros da IA: {base_queryset.count()}") # DEBUG

        serializer = ImovelPublicSerializer(base_queryset, many=True)

        mensagem_resposta = search_params.get('mensagem_resposta', "Resultados da sua pesquisa com IA.")
        if not base_queryset.exists():
            mensagem_resposta = "Não encontrei nenhum imóvel que corresponda à sua procura. Tente refinar a sua pesquisa."

        return Response({
            "mensagem": mensagem_resposta,
            "imoveis": serializer.data
        }, status=status.HTTP_200_OK)


class ImovelPublicDetailView(RetrieveAPIView):
    """
    View para detalhar um imóvel específico no site público.
    """
    serializer_class = ImovelPublicSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Imovel.objects.filter(publicado_no_site=True) # Filtro base
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


# ===================================================================
# VIEWS INTERNAS (Para o painel administrativo, requerem login)
# ===================================================================

class ImovelViewSet(viewsets.ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['logradouro', 'cidade', 'titulo_anuncio', 'codigo_referencia', 'bairro'] # Adicionado bairro aqui também

    def get_queryset(self):
        if self.request.user.is_superuser:
             base_queryset = Imovel.objects.all()
        elif self.request.tenant:
            base_queryset = Imovel.objects.filter(imobiliaria=self.request.tenant)
        else:
            return Imovel.objects.none()

        status_param = self.request.query_params.get('status', None)
        if self.action == 'list':
            if not status_param:
                 base_queryset = base_queryset.exclude(status=Imovel.Status.DESATIVADO)
            else:
                 base_queryset = base_queryset.filter(status=status_param)

        finalidade = self.request.query_params.get('finalidade', None)
        tipo = self.request.query_params.get('tipo', None)
        cidade = self.request.query_params.get('cidade', None)
        bairro = self.request.query_params.get('bairro', None) # Filtro de bairro para o painel

        if finalidade: base_queryset = base_queryset.filter(finalidade=finalidade)
        if tipo: base_queryset = base_queryset.filter(tipo=tipo)
        if cidade: base_queryset = base_queryset.filter(cidade__icontains=cidade)
        if bairro: base_queryset = base_queryset.filter(bairro__icontains=bairro) # Adicionado filtro de bairro

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


    def _get_imovel_contexto_para_ia(self, imovel):
        """Helper para formatar os dados do imóvel para a IA."""
        
        contexto = []
        contexto.append(f"Tipo de Imóvel: {imovel.get_tipo_display()}")
        contexto.append(f"Finalidade: {imovel.get_finalidade_display()}")
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

        # 1. Obter o prompt de DESCRIÇÃO da base de dados
        try:
            prompt_config = ModeloDePrompt.objects.get(em_uso_descricao=True)
            template_prompt = prompt_config.template_do_prompt
        except ModeloDePrompt.DoesNotExist:
            return Response(
                {"error": "Nenhum modelo de prompt para 'Geração de Descrição' está ativo no sistema."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 2. Obter a "Voz da Marca" da imobiliária (se existir)
        # CORREÇÃO ANTERIOR: Forçamos a conversão para STR() para evitar o TypeError.
        voz_da_marca_obj = imovel.imobiliaria.voz_da_marca_preferida
        if voz_da_marca_obj:
            voz_da_marca = str(voz_da_marca_obj)
        else:
            voz_da_marca = "um tom profissional e convidativo"
        
        # 3. Formatar os dados do imóvel
        imovel_data = self._get_imovel_contexto_para_ia(imovel)
        
        # 4. Substituir os placeholders no prompt
        prompt_final = template_prompt.replace('{{imovel_data}}', imovel_data)
        prompt_final = prompt_final.replace('{{voz_da_marca}}', voz_da_marca)

        print(f"--- Gerando Descrição IA para Imóvel {imovel.id} ---")
        print(f"Prompt Final:\n{prompt_final}")
        print("-------------------------------------------------")

        # 5. Enviar para a API da IA
        try:
            if not api_key:
                 raise ValueError("GOOGLE_API_KEY não está configurada no servidor.")

            model_name = 'models/gemini-flash-latest'
            model = genai.GenerativeModel(model_name)
            
            # Configuração para garantir que a IA não seja muito restritiva
            generation_config = genai.types.GenerationConfig(
                temperature=0.7, # Um pouco mais criativo
            )
            
            response = model.generate_content(prompt_final, generation_config=generation_config)

            if not response.parts:
                 raise ValueError("Resposta inesperada da IA (sem 'parts').")

            generated_text = response.parts[0].text
            
            # Limpeza básica do texto
            generated_text = generated_text.strip().lstrip('```markdown').lstrip('```').rstrip('```').strip()
            
            # --- CORREÇÃO SOLICITADA: Remoção do prefixo "Título Sugerido:" ---
            prefixo = 'título sugerido:'
            
            if generated_text.lower().startswith(prefixo):
                 # Se o texto começar com o prefixo, tentamos remover a linha inteira.
                 if '\n' in generated_text:
                      # Remove a primeira linha inteira (que contém o título sugerido)
                      generated_text = generated_text.split('\n', 1)[1].strip()
                 else:
                      # Se for apenas uma linha (e contém o prefixo), removemos apenas o prefixo
                      generated_text = generated_text[len(prefixo):].lstrip(':').strip()
                      
            # Limpeza final (caso a remoção tenha deixado espaços no início)
            generated_text = generated_text.strip()
            # --- FIM DA CORREÇÃO SOLICITADA ---

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
            # Filtra imagens pela imobiliária do imóvel associado
            return ImagemImovel.objects.filter(imovel__imobiliaria=self.request.tenant)
        return ImagemImovel.objects.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        imovel_id = request.data.get('imovel')
        if not imovel_id:
            return Response({'imovel': ['O ID do imóvel é obrigatório.']}, status=status.HTTP_400_BAD_REQUEST)

        # Garante que o imóvel pertence ao tenant do usuário (ou é superuser)
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
         # Garante que a imagem pertence a um imóvel do tenant (ou é superuser)
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

        # Garante que o imóvel pertence ao tenant
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
             # Alguns IDs fornecidos não correspondem a imagens válidas para este imóvel/tenant
             raise PermissionDenied("Uma ou mais imagens fornecidas são inválidas ou não pertencem a este imóvel.")

        updated_instances = []
        for index, image_id_str in enumerate(ordem_ids):
            image_id = int(image_id_str)
            if image_id in imagens_map: # Confirma novamente, embora a verificação anterior deva bastar
                img = imagens_map[image_id]
                img.ordem = index
                img.principal = (index == 0)
                updated_instances.append(img)
            else:
                 # Log interno para caso algo muito estranho ocorra
                 print(f"Alerta CRÍTICO: ID de imagem {image_id} não encontrado no mapeamento durante reordenação, APÓS validação inicial.")

        # Usa bulk_update para eficiência
        ImagemImovel.objects.bulk_update(updated_instances, ['ordem', 'principal'])
        return Response({'status': 'Ordem das imagens atualizada com sucesso.'}, status=status.HTTP_200_OK)


class ContatoImovelViewSet(viewsets.ModelViewSet):
    queryset = ContatoImovel.objects.all()
    serializer_class = ContatoImovelSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy', 'arquivar']:
            self.permission_classes = [permissions.IsAuthenticated]
        else: # create
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def get_queryset(self):
        base_queryset = ContatoImovel.objects.filter(arquivado=False)
        if self.request.user.is_superuser:
            return base_queryset.all().order_by('-data_criacao')
        elif self.request.user.is_authenticated and self.request.tenant:
            # Filtra contatos pela imobiliária do imóvel associado
            return base_queryset.filter(imovel__imobiliaria=self.request.tenant).order_by('-data_criacao')
        return ContatoImovel.objects.none()

    def perform_create(self, serializer):
        contato = serializer.save()
        try:
            imobiliaria = contato.imovel.imobiliaria
            if hasattr(imobiliaria, 'email_contato') and imobiliaria.email_contato:
                destinatario_email = imobiliaria.email_contato
                assunto = f"Novo Contato para o Imóvel: {contato.imovel.titulo_anuncio or contato.imovel.logradouro}"
                # Construir URL base dinamicamente seria ideal, mas por agora usamos um placeholder
                base_url_painel = "http://localhost:5173" # Ou a URL de produção
                link_imovel_painel = f"{base_url_painel}/imoveis/editar/{contato.imovel.id}"

                mensagem_corpo = f"""
                Você recebeu um novo contato através do site!

                Imóvel: {contato.imovel.titulo_anuncio or contato.imovel.logradouro} (Ref: {contato.imovel.codigo_referencia})
                Link do Imóvel no Painel: {link_imovel_painel}

                Nome do Interessado: {contato.nome}
                Email: {contato.email}
                Telefone: {contato.telefone or 'Não informado'}

                Mensagem:
                {contato.mensagem}

                ---
                Enviado por ImobCloud
                """
                remetente = settings.DEFAULT_FROM_EMAIL
                send_mail(assunto, mensagem_corpo, remetente, [destinatario_email], fail_silently=False)
                # print(f"Email de contato enviado para {destinatario_email}") # DEBUG

            oportunidade_associada = Oportunidade.objects.filter(imovel=contato.imovel).first()
            if oportunidade_associada and oportunidade_associada.responsavel:
                destinatario_notificacao = oportunidade_associada.responsavel.user
                Notificacao.objects.create(
                    destinatario=destinatario_notificacao,
                    mensagem=f"Novo contato de '{contato.nome}' para o imóvel '{contato.imovel.titulo_anuncio or contato.imovel.logradouro}'.",
                    link=f"/contatos" # Idealmente, link direto para o contato: /contatos?id={contato.id}
                )
                # print(f"Notificação criada para o responsável: {destinatario_notificacao.username}") # DEBUG
            # else:
                 # print("Nenhuma oportunidade ou responsável encontrado para notificação.") # DEBUG

        except Exception as e:
            print(f"ERRO AO ENVIAR NOTIFICAÇÕES DE CONTATO: {e}")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def arquivar(self, request, pk=None):
        # get_object() já filtra pelo tenant/superuser devido ao get_queryset
        contato = self.get_object()
        contato.arquivado = True
        contato.save()
        return Response({'status': 'Contacto arquivado com sucesso'}, status=status.HTTP_200_OK)


class GerarAutorizacaoPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, imovel_id, *args, **kwargs):
        # Garante que o imóvel pertence ao tenant ou que é superuser
        try:
            if request.user.is_superuser:
                 imovel = Imovel.objects.get(pk=imovel_id)
            elif request.tenant:
                 imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=request.tenant)
            else:
                 raise PermissionDenied("Tenant não identificado.")
        except Imovel.DoesNotExist:
             raise Http404("Imóvel não encontrado ou não pertence à sua imobiliária.")

        if not imovel.proprietario:
            return HttpResponse("Erro: O imóvel não possui um proprietário vinculado.", status=400)

        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except locale.Error:
            try:
                 locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
            except locale.Error:
                 print("Aviso: Locale 'pt_BR.UTF-8' e 'Portuguese_Brazil.1252' não encontrados. Usando locale padrão.")

        hoje = date.today()
        finalidade_texto = imovel.get_finalidade_display() # Usa o display do ChoiceField
        valor = imovel.valor_venda if imovel.finalidade == Imovel.Finalidade.A_VENDA else imovel.valor_aluguel
        valor = valor or Decimal(0)
        reais = int(valor)
        centavos = int((valor - reais) * 100)
        valor_por_extenso = num2words(reais, lang='pt_BR') + " reais"
        if centavos > 0:
            valor_por_extenso += " e " + num2words(centavos, lang='pt_BR') + " centavos"

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
            'comissao_percentual': imovel.comissao_percentual or 0,
            'comissao_por_extenso': num2words(imovel.comissao_percentual or 0, lang='pt_BR') + " por cento",
            'data_hoje': hoje,
            'dia_hoje': hoje.day,
            'mes_hoje': hoje.strftime("%B"),
            'ano_hoje': hoje.year,
            'data_fim_autorizacao_formatada': imovel.data_fim_autorizacao.strftime("%d de %B de %Y") if imovel.data_fim_autorizacao else "INDETERMINADO"
        }
        html_string = render_to_string('autorizacao_template.html', context)
        result = BytesIO()

        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result, encoding='UTF-8')

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f'autorizacao_{finalidade_texto.lower()}_imovel_{imovel.codigo_referencia or imovel.id}.pdf'
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
             print(f"Erro ao gerar PDF para imóvel {imovel.id}: {pdf.err}")
             return HttpResponse(f"Erro ao gerar o PDF: {pdf.err}", status=500)


class AutorizacaoStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser] # Apenas Admin ou Superuser

    def get(self, request, *args, **kwargs):
        # A permissão IsAdminUser já garante que é admin ou superuser
        tenant = request.tenant
        if not tenant and request.user.is_superuser:
            # Para superuser sem tenant específico, talvez listar todos ou o primeiro?
            # Por agora, vamos retornar erro se não houver tenant claro.
             tenant = Imobiliaria.objects.first() # Ou outra lógica para superuser
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
    """
    View para detalhar a imobiliária pública (usando subdominio como lookup).
    """
    queryset = Imobiliaria.objects.all()
    serializer_class = ImobiliariaPublicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'subdominio'
    lookup_url_kwarg = 'pk'

    def get_object(self):
        # Removendo prints de depuração
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
             print(f"Erro inesperado ao buscar imobiliária: {e}") # Mantido para erros gerais
             raise Http404("Erro ao buscar dados da imobiliária.")
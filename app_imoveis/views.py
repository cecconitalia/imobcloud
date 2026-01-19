# C:\wamp64\www\ImobCloud\app_imoveis\views.py

import os
import json
import requests
import traceback
import locale
from decimal import Decimal, InvalidOperation
from datetime import date, timedelta
from io import BytesIO

from django.db import models, transaction, OperationalError
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, QueryDict, Http404 
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Count, Q, Case, When, Value, CharField, Max, F, ExpressionWrapper, fields, Sum 
from django.conf import settings
from django.core.mail import send_mail

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView

from xhtml2pdf import pisa
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

try:
    from num2words import num2words
except ImportError:
    num2words = None

from .models import Imovel, ImagemImovel, ContatoImovel
from .serializers import (
    ImovelSerializer, 
    ImovelPublicSerializer, 
    ContatoImovelSerializer, 
    ImagemImovelSerializer,
    ImovelSimplificadoSerializer 
)
from core.models import Imobiliaria, PerfilUsuario, Notificacao, ConfiguracaoGlobal
from app_clientes.models import Cliente, Oportunidade 
from app_config_ia.models import ModeloDePrompt
from core.serializers import ImobiliariaPublicSerializer

# ===================================================================
# FUNÇÕES AUXILIARES
# ===================================================================

def traduzir_mes(nome_mes_ingles):
    mapa = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
        'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
        'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
        'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }
    return mapa.get(nome_mes_ingles, nome_mes_ingles)

def get_autorizacao_context(imovel):
    """
    Gera o contexto de dados para renderizar a autorização de venda/aluguel.
    """
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    except locale.Error:
        try:
             locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252')
        except locale.Error:
             pass 

    hoje = date.today()
    finalidade_texto = imovel.get_finalidade_display() 
    valor = imovel.valor_venda if imovel.status == 'A_VENDA' else imovel.valor_aluguel
    valor = valor or Decimal(0)
    reais = int(valor)
    centavos = int((valor - reais) * 100)
    
    valor_por_extenso = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if num2words:
        try:
            valor_por_extenso_txt = num2words(reais, lang='pt_BR') + " reais"
            if centavos > 0:
                 valor_por_extenso_txt += " e " + num2words(centavos, lang='pt_BR') + " centavos"
            valor_por_extenso = f"{valor_por_extenso} ({valor_por_extenso_txt})"
        except:
            pass
    
    comissao = imovel.comissao_percentual or Decimal(0)
    comissao_por_extenso = f"{comissao}%"
    if num2words:
        try:
            comissao_por_extenso_txt = num2words(float(comissao), lang='pt_BR') + " por cento"
            comissao_por_extenso = f"{comissao}% ({comissao_por_extenso_txt})"
        except:
            pass

    proprietario = imovel.proprietario
    nome_proprietario = ""
    if proprietario:
        nome_proprietario = proprietario.razao_social if proprietario.tipo_pessoa == 'JURIDICA' and proprietario.razao_social else proprietario.nome

    mes_hoje = traduzir_mes(hoje.strftime("%B"))
    
    data_fim_fmt = "INDETERMINADO"
    if imovel.data_fim_autorizacao:
        mes_fim = traduzir_mes(imovel.data_fim_autorizacao.strftime("%B"))
        data_fim_fmt = f"{imovel.data_fim_autorizacao.day} de {mes_fim} de {imovel.data_fim_autorizacao.year}"

    return {
        'imovel': imovel,
        'proprietario': proprietario,
        'nome_proprietario': nome_proprietario,
        'imobiliaria': imovel.imobiliaria,
        'finalidade_texto': finalidade_texto,
        'valor': valor,
        'valor_por_extenso': valor_por_extenso,
        'comissao_percentual': comissao, 
        'comissao_por_extenso': comissao_por_extenso,
        'informacoes_adicionais': imovel.informacoes_adicionais_autorizacao, 
        'data_hoje': hoje,
        'dia_hoje': hoje.day,
        'mes_hoje': mes_hoje,
        'ano_hoje': hoje.year,
        'data_fim_autorizacao_formatada': data_fim_fmt
    }

def get_imovel_seguro(request, pk):
    tenant = getattr(request, 'tenant', None) or getattr(request.user, 'imobiliaria', None)
    
    try:
        if request.user.is_superuser:
             if tenant:
                 return Imovel.objects.get(pk=pk, imobiliaria=tenant)
             else:
                 return Imovel.objects.get(pk=pk)
        elif tenant:
             return Imovel.objects.get(pk=pk, imobiliaria=tenant)
        else:
             raise PermissionDenied("Tenant não identificado.")
    except Imovel.DoesNotExist:
         raise Http404("Imóvel não encontrado ou não pertence à sua imobiliária.")

# ===================================================================
# VIEWS DE EDITOR DE AUTORIZAÇÃO
# ===================================================================

class GetAutorizacaoHtmlView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        imovel = get_imovel_seguro(request, pk)
        
        if imovel.conteudo_html_autorizacao:
            return HttpResponse(imovel.conteudo_html_autorizacao)
        
        context = get_autorizacao_context(imovel)
        try:
            html_content = render_to_string('autorizacao_template.html', context)
        except Exception as e:
            return HttpResponse(f"<h1>Autorização de Venda/Aluguel</h1><p>Imóvel: {imovel.titulo_anuncio}</p><p>Erro ao carregar template: {str(e)}</p>")
            
        return HttpResponse(html_content)

class SalvarAutorizacaoHtmlView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        imovel = get_imovel_seguro(request, pk)
        
        html_content = request.data.get('html_content')
        if not html_content:
            return Response({'error': 'Conteúdo HTML não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        imovel.conteudo_html_autorizacao = html_content
        imovel.save()
        
        return Response({'status': 'Autorização salva com sucesso.'}, status=status.HTTP_200_OK)

class VisualizarAutorizacaoPdfView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        imovel = get_imovel_seguro(request, pk)
        
        if imovel.conteudo_html_autorizacao:
            raw_html = imovel.conteudo_html_autorizacao
        else:
            context = get_autorizacao_context(imovel)
            try:
                raw_html = render_to_string('autorizacao_template.html', context)
            except:
                raw_html = f"<p>Erro: Template ausente.</p>"

        if "<html>" not in raw_html.lower():
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <style>
                    @page {{
                        size: A4;
                        margin: 2cm;
                        @frame footer_frame {{
                            -pdf-frame-content: footerContent;
                            bottom: 1cm;
                            margin-left: 2cm;
                            margin-right: 2cm;
                            height: 1cm;
                        }}
                    }}
                    body {{
                        font-family: Helvetica, sans-serif;
                        font-size: 11pt;
                        line-height: 1.5;
                        color: #333333;
                    }}
                    h1 {{ font-size: 16pt; text-align: center; color: #000; margin-bottom: 20px; }}
                    h2 {{ font-size: 13pt; margin-top: 15px; border-bottom: 1px solid #ccc; }}
                    p {{ text-align: justify; margin-bottom: 10px; }}
                    ul {{ margin-left: 20px; }}
                </style>
            </head>
            <body>
                {raw_html}
                <div id="footerContent" style="text-align: center; font-size: 9pt; color: #777;">
                    Documento gerado pelo sistema ImobCloud
                </div>
            </body>
            </html>
            """
        else:
            full_html = raw_html
            if "charset=utf-8" not in full_html.lower():
                full_html = full_html.replace("<head>", '<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">')

        result = BytesIO()
        pdf = pisa.pisaDocument(
            src=BytesIO(full_html.encode("UTF-8")), 
            dest=result, 
            encoding='UTF-8'
        )

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f'autorizacao_imovel_{imovel.codigo_referencia or imovel.id}.pdf'
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        else:
            return HttpResponse(f"Erro ao gerar o PDF: {pdf.err}", status=500)

# ===================================================================
# VIEWS PÚBLICAS EXISTENTES
# ===================================================================

class ImovelPublicListView(ListAPIView):
    serializer_class = ImovelPublicSerializer
    permission_classes = [permissions.AllowAny]
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
        search = self.request.query_params.get('search', None) 

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

        if search:
            base_queryset = base_queryset.filter(
                Q(titulo_anuncio__icontains=search) |
                Q(descricao_completa__icontains=search) |
                Q(cidade__icontains=search) |
                Q(bairro__icontains=search) |
                Q(codigo_referencia__icontains=search)
            )

        if finalidade: base_queryset = base_queryset.filter(finalidade=finalidade)
        if tipo: base_queryset = base_queryset.filter(tipo=tipo)
        if cidade: base_queryset = base_queryset.filter(cidade__icontains=cidade)
        if valor_min:
            q_filter = Q(valor_venda__gte=valor_min) if status_param == 'A_VENDA' else Q(valor_aluguel__gte=valor_min)
            base_queryset = base_queryset.filter(q_filter)
        if valor_max:
            q_filter = Q(valor_venda__lte=valor_max) if status_param == 'A_VENDA' else Q(valor_aluguel__lte=valor_max)
            base_queryset = base_queryset.filter(q_filter)
        if quartos_min: base_queryset = base_queryset.filter(quartos__gte=quartos_min)
        if vagas_min: base_queryset = base_queryset.filter(vagas_garagem__gte=vagas_min)
        if aceita_pet: base_queryset = base_queryset.filter(aceita_pet=True)
        if mobiliado: base_queryset = base_queryset.filter(mobiliado=True)
        if piscina: base_queryset = base_queryset.filter(Q(piscina_privativa=True) | Q(piscina_condominio=True))
        
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

    def _processar_busca_ia(self, request):
        try:
            user_query = request.data.get('query') or request.query_params.get('query')
            subdomain_param = request.query_params.get('subdomain', None)

            if not user_query:
                return Response({
                    "mensagem": "Por favor, descreva o imóvel que você procura.",
                    "imoveis": []
                }, status=status.HTTP_200_OK)

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
                    "mensagem": "Subdomínio não fornecido.",
                    "imoveis": []
                 }, status=status.HTTP_400_BAD_REQUEST)

            # --- CORREÇÃO AQUI: Tenta buscar google_gemini_api_key primeiro, depois google_api_key global ---
            chave_banco = getattr(imobiliaria_obj, 'google_gemini_api_key', None)
            if not chave_banco:
                 # Tenta buscar nas configurações globais
                 try:
                     config = ConfiguracaoGlobal.objects.first()
                     if config:
                         chave_banco = config.google_api_key
                 except:
                     pass
            
            chave_env = os.getenv("GOOGLE_API_KEY")
            api_key = str(chave_banco).strip() if chave_banco else chave_env

            if not api_key:
                return Response(
                    {"error": "Chave de API não configurada no Admin."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            genai.configure(api_key=api_key)
            
            try:
                prompt_config = ModeloDePrompt.objects.get(em_uso_busca=True)
                template_prompt = prompt_config.template_do_prompt
                preferred_model = prompt_config.modelo_api if hasattr(prompt_config, 'modelo_api') else None
            except (ModeloDePrompt.DoesNotExist, OperationalError):
                template_prompt = "Você é um assistente de busca de imóveis. O usuário quer: {{user_query}}"
                preferred_model = None
            
            json_instructions = """
            RETORNE APENAS JSON:
            {
                "busca_valida": true,
                "status": "A_VENDA" | "PARA_ALUGAR" | null,
                "tipo": "CASA" | "APARTAMENTO" | "TERRENO" | "SALA_COMERCIAL" | null,
                "cidade": "Nome" | null,
                "bairro": "Nome" | null,
                "valor_min": number | null,
                "valor_max": number | null,
                "quartos_min": number | null,
                "vagas_min": number | null,
                "mensagem_resposta": "Texto curto"
            }
            """
            prompt_final = template_prompt.replace('{{user_query}}', user_query)
            prompt_final = prompt_final.replace('{{imovel_data}}', '') 
            prompt_final += json_instructions

            search_params = {}
            last_error = ""

            models_to_try = []
            if preferred_model:
                models_to_try.append(preferred_model)
                if not preferred_model.startswith('models/'):
                    models_to_try.append(f"models/{preferred_model}")
            
            # Priorizando 1.5-flash
            defaults = ['models/gemini-1.5-flash', 'gemini-1.5-flash', 'models/gemini-2.0-flash', 'gemini-2.0-flash', 'models/gemini-pro']
            for m in defaults:
                if m not in models_to_try:
                    models_to_try.append(m)

            def try_generate(model_tag):
                model = genai.GenerativeModel(model_tag)
                try:
                    response = model.generate_content(prompt_final, generation_config={"response_mime_type": "application/json"})
                except:
                    response = model.generate_content(prompt_final)
                    
                if not response.parts: raise ValueError("Resposta vazia")
                return response.parts[0].text

            json_text_raw = None
            
            for model_name in models_to_try:
                try:
                    json_text_raw = try_generate(model_name)
                    break 
                except Exception as e:
                    last_error = str(e)
                    continue

            if not json_text_raw:
                 return Response(
                     {"error": f"Falha na IA. Último erro: {last_error}"}, 
                     status=status.HTTP_503_SERVICE_UNAVAILABLE
                 )

            try:
                json_text = json_text_raw.strip()
                if "```json" in json_text:
                    json_text = json_text.split("```json")[1].split("```")[0].strip()
                elif "```" in json_text:
                    json_text = json_text.split("```")[1].split("```")[0].strip()
                
                search_params = json.loads(json_text)

            except json.JSONDecodeError:
                 return Response({
                     "mensagem": "Não consegui entender. Tente simplificar.",
                     "imoveis": []
                 }, status=status.HTTP_200_OK)

            base_queryset = Imovel.objects.filter(
                imobiliaria=imobiliaria_obj,
                publicado_no_site=True
            ).exclude(status='DESATIVADO')

            if search_params.get('busca_valida') is False:
                return Response({
                     "mensagem": search_params.get('mensagem_resposta', "Não entendi sua busca."),
                     "imoveis": []
                }, status=status.HTTP_200_OK)
            
            status_ia = search_params.get('status')
            if status_ia:
                 status_map = { 'A_VENDA': 'A_VENDA', 'VENDA': 'A_VENDA', 'PARA_ALUGAR': 'PARA_ALUGAR', 'ALUGUEL': 'PARA_ALUGAR' }
                 db_status = status_map.get(status_ia.upper())
                 if db_status: base_queryset = base_queryset.filter(status=db_status)

            tipo_ia = search_params.get('tipo')
            if tipo_ia:
                tipo_upper = tipo_ia.upper().replace(' ', '_')
                base_queryset = base_queryset.filter(tipo=tipo_upper)

            cidade_ia = search_params.get('cidade')
            if cidade_ia: base_queryset = base_queryset.filter(cidade__icontains=cidade_ia)

            bairro_ia = search_params.get('bairro')
            if bairro_ia: base_queryset = base_queryset.filter(bairro__icontains=bairro_ia)

            valor_min = search_params.get('valor_min')
            valor_max = search_params.get('valor_max')
            
            if valor_min or valor_max:
                qs_venda = Q()
                qs_aluguel = Q()
                if valor_min:
                    qs_venda &= Q(valor_venda__gte=valor_min)
                    qs_aluguel &= Q(valor_aluguel__gte=valor_min)
                if valor_max:
                    qs_venda &= Q(valor_venda__lte=valor_max)
                    qs_aluguel &= Q(valor_aluguel__lte=valor_max)

                if status_ia == 'A_VENDA': base_queryset = base_queryset.filter(qs_venda)
                elif status_ia == 'PARA_ALUGAR': base_queryset = base_queryset.filter(qs_aluguel)
                else: base_queryset = base_queryset.filter(qs_venda | qs_aluguel)

            if search_params.get('quartos_min'): base_queryset = base_queryset.filter(quartos__gte=search_params['quartos_min'])
            if search_params.get('vagas_min'): base_queryset = base_queryset.filter(vagas_garagem__gte=search_params['vagas_min'])
            if search_params.get('piscina'): base_queryset = base_queryset.filter(Q(piscina_privativa=True) | Q(piscina_condominio=True))
            if search_params.get('aceita_pet'): base_queryset = base_queryset.filter(aceita_pet=True)
            if search_params.get('mobiliado'): base_queryset = base_queryset.filter(mobiliado=True)

            serializer = ImovelPublicSerializer(base_queryset, many=True)
            
            mensagem_resposta = search_params.get('mensagem_resposta', "Resultados da busca:")
            if not base_queryset.exists():
                mensagem_resposta += f" (Nenhum imóvel encontrado. Filtros: {cidade_ia or 'Qualquer cidade'}, {status_ia or 'Qualquer status'})"

            return Response({
                "mensagem": mensagem_resposta,
                "imoveis": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            traceback.print_exc()
            return Response({"error": f"Erro interno ao processar IA: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        return self._processar_busca_ia(request)

    def get(self, request, *args, **kwargs):
        return self._processar_busca_ia(request)


# ===================================================================
# VIEWS INTERNAS EXISTENTES
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
        
        tenant = getattr(self.request, 'tenant', None)
        if not tenant and hasattr(user, 'imobiliaria'):
            tenant = user.imobiliaria

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
             base_queryset = base_queryset.exclude(status='DESATIVADO')

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
        tenant = getattr(self.request, 'tenant', None)
        if not tenant and hasattr(self.request.user, 'imobiliaria'):
            tenant = self.request.user.imobiliaria
            
        if self.request.user.is_superuser:
            if 'imobiliaria' in self.request.data:
                imobiliaria_id = self.request.data['imobiliaria']
                imobiliaria_obj = get_object_or_404(Imobiliaria, pk=imobiliaria_id)
                serializer.save(imobiliaria=imobiliaria_obj)
                return

            if tenant:
                serializer.save(imobiliaria=tenant)
                return

            first_tenant = Imobiliaria.objects.first()
            if first_tenant:
                serializer.save(imobiliaria=first_tenant)
                return
            else:
                raise PermissionDenied("Nenhuma imobiliária cadastrada no sistema.")

        elif tenant:
            serializer.save(imobiliaria=tenant)
        else:
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
             instance.status = 'DESATIVADO' 
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
        
        STATUS_A_VENDA = 'A_VENDA'
        STATUS_PARA_ALUGAR = 'PARA_ALUGAR'
        
        if imovel.valor_venda and imovel.status == STATUS_A_VENDA:
            contexto.append(f"Valor de Venda: R$ {imovel.valor_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        if imovel.valor_aluguel and imovel.status == STATUS_PARA_ALUGAR:
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

    @action(detail=True, methods=['post', 'get'], url_path='gerar-descricao-ia')
    def gerar_descricao_ia(self, request, pk=None):
        try:
            imovel = self.get_object()
        except Exception as e:
             return Response({"error": f"Imóvel não encontrado: {e}"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # CORREÇÃO: Tenta pegar a chave correta 'google_gemini_api_key' da imobiliária
            api_key = getattr(imovel.imobiliaria, 'google_gemini_api_key', None)
            
            # Se não tiver, tenta a configuração global
            if not api_key:
                try:
                    config = ConfiguracaoGlobal.objects.first()
                    if config:
                        api_key = config.google_api_key
                except:
                    pass

            # Por fim, tenta do ambiente
            if not api_key:
                api_key = os.getenv("GOOGLE_API_KEY")

            if not api_key:
                return Response(
                    {"error": "Chave de API do Google (Gemini) não configurada. Configure na Imobiliária ou nas Configurações Globais."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            genai.configure(api_key=api_key)

            model_name = 'gemini-1.5-flash'
            
            try:
                prompt_config = ModeloDePrompt.objects.get(em_uso_descricao=True)
                template_prompt = prompt_config.template_do_prompt
                
                if hasattr(prompt_config, 'modelo_api') and prompt_config.modelo_api:
                    model_name = prompt_config.modelo_api.replace("models/", "")
            except Exception:
                template_prompt = "Escreva uma descrição imobiliária com voz {{voz_da_marca}} para: {{imovel_data}}"
        
            voz_da_marca_obj = imovel.imobiliaria.voz_da_marca_preferida
            voz_da_marca = str(voz_da_marca_obj) if voz_da_marca_obj else "um tom profissional e convidativo"
            
            imovel_data = self._get_imovel_contexto_para_ia(imovel)
            
            prompt_final = template_prompt.replace('{{imovel_data}}', imovel_data)
            prompt_final = prompt_final.replace('{{voz_da_marca}}', voz_da_marca)

            generated_text = None
            # Prioriza 1.5-flash que é mais estável
            models_to_try = ['gemini-1.5-flash', model_name, 'gemini-2.0-flash', 'gemini-1.0-pro']
            
            errors = []
            for m_tag in models_to_try:
                try:
                    model = genai.GenerativeModel(m_tag)
                    response = model.generate_content(prompt_final)
                    if response.parts:
                        generated_text = response.parts[0].text
                        break
                except Exception as e:
                    errors.append(f"{m_tag}: {str(e)}")
                    continue

            if not generated_text:
                 raise ValueError(f"Todos os modelos falharam ao gerar a descrição. Detalhes: {'; '.join(errors)}")

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
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy', 'arquivar']:
            self.permission_classes = [permissions.IsAuthenticated]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def get_queryset(self):
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
        dados = serializer.validated_data
        if not dados.get('telefone'):
             raise ValidationError({"telefone": ["Este campo é obrigatório para o contato."]})

        contato = serializer.save()
        imovel = contato.imovel
        imobiliaria = imovel.imobiliaria
        
        cliente_para_oportunidade = None
        oportunidade = None

        cliente_por_email = Cliente.objects.filter(imobiliaria=imobiliaria, email__iexact=contato.email).first()

        if cliente_por_email:
            cliente_para_oportunidade = cliente_por_email
            
        else:
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
                 
                 responsavel = oportunidade.responsavel
                 if not responsavel:
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
                base_url_painel = "http://localhost:5173" 
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

    def get(self, request, imovel_id, *args, **kwargs):
        # Esta view agora pode ser usada apenas como fallback ou para gerar direto do modelo antigo
        # Se quiser usar o novo sistema, o frontend deve chamar VisualizarAutorizacaoPdfView
        # Mas mantemos para compatibilidade se necessário
        
        # Reutilizando a lógica da nova view para evitar duplicação
        view = VisualizarAutorizacaoPdfView()
        # Injeta o request na view instanciada
        view.setup(request, *args, **kwargs)
        return view.get(request, pk=imovel_id)

    def post(self, request, imovel_id, *args, **kwargs):
        # O POST anterior salvava dados e gerava PDF
        # Agora o salvamento é via SalvarAutorizacaoHtmlView
        # Podemos manter isso funcionando redirecionando logicamente ou deprecando
        return HttpResponse("Use os novos endpoints de editor.", status=400)


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

        base_queryset = Imovel.objects.filter(imobiliaria=tenant).exclude(status='DESATIVADO')

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

def _get_autorizacao_queryset(tenant, query_params): 
    queryset = Imovel.objects.filter(
        imobiliaria=tenant
    ).exclude(status='DESATIVADO').select_related('proprietario')
    
    today = date.today()
    trinta_dias = today + timedelta(days=30)
    
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

    dias_timedelta = ExpressionWrapper(F('data_fim_autorizacao') - today, output_field=fields.DurationField())
    queryset = queryset.annotate(dias_restantes=dias_timedelta).order_by('data_fim_autorizacao')

    data_list = []
    total_imoveis = 0
    total_expirados = 0
    total_venda_potencial = Decimal(0)
    total_aluguel_potencial = Decimal(0)

    for imovel in queryset:
        if imovel.data_fim_autorizacao and imovel.dias_restantes:
             dias_restantes = imovel.dias_restantes.days
        else:
             dias_restantes = 9999 
        
        status_risco = 'Ativo'
        if imovel.data_fim_autorizacao and dias_restantes < 0:
             status_risco = 'Expirado'
             total_expirados += 1
        elif imovel.data_fim_autorizacao and dias_restantes <= 30:
             status_risco = 'Risco (30 dias)'
        
        total_imoveis += 1
        
        if imovel.valor_venda: total_venda_potencial += imovel.valor_venda
        if imovel.valor_aluguel: total_aluguel_potencial += imovel.valor_aluguel
        
        def fmt_money(val):
            return f"{val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.') if val else "-"

        nome_proprietario = 'N/A'
        telefone_proprietario = '-'
        email_proprietario = '-'
        
        if imovel.proprietario:
            p = imovel.proprietario
            nome_proprietario = p.razao_social if p.tipo_pessoa == 'JURIDICA' and p.razao_social else p.nome
            telefone_proprietario = p.telefone or p.celular or '-'
            email_proprietario = p.email or '-'

        finalidade_display = "Venda" if imovel.status == 'A_VENDA' else "Aluguel"
        if imovel.status not in ['A_VENDA', 'PARA_ALUGAR']:
             finalidade_display = imovel.get_status_display()

        data_list.append({
            'id': imovel.id, 
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
        tenant = getattr(request, 'tenant', None) or getattr(request.user, 'imobiliaria', None)
        
        if not tenant and request.user.is_superuser:
            tenant = Imobiliaria.objects.first()
        
        if not tenant:
            return HttpResponse("Erro: Nenhuma imobiliária identificada.", status=400)

        data_structure = _get_autorizacao_queryset(tenant, request.query_params) 
        data = data_structure['list']
        summary = data_structure['summary']
        
        titulo_relatorio = "Relatório de Autorizações"
        
        status_vigencia = request.query_params.get('status_vigencia')
        tipo_negocio = request.query_params.get('tipo_negocio')
        
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

        context = {
            'data': data,
            'summary': summary,
            'titulo_relatorio': titulo_relatorio,
            'data_geracao': timezone.now(), 
            'imobiliaria': tenant,
            'usuario_solicitante': request.user.first_name or request.user.username
        }

        html_string = render_to_string('relatorio_autorizacoes_template.html', context)
        
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result, encoding='UTF-8')

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f'relatorio_autorizacoes_{timezone.now().strftime("%Y-%m-%d")}.pdf'
            
            response['Content-Disposition'] = f'inline; filename="{filename}"' 
            return response
        else:
            return HttpResponse(f"Erro ao gerar o PDF: {pdf.err}", status=500)
# C:\wamp64\www\imobcloud\app_publicacoes\views.py

import os
import requests
import google.generativeai as genai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from app_imoveis.models import Imovel, ImagemImovel
from .models import PublicacaoSocial, PostAgendado, PublicacaoHistorico
from app_config_ia.models import ModeloDePrompt
from core.models import Imobiliaria
from rest_framework import viewsets
from .serializers import PostAgendadoSerializer, PublicacaoHistoricoSerializer
from app_imoveis.serializers import ImovelSerializer

# Importa a tarefa Celery, resolvendo a importação circular
from .tasks import publicar_post_agendado

# --- IMPORTAÇÕES ADICIONADAS PARA TRATAR O FUSO HORÁRIO ---
from django.utils import timezone
from datetime import datetime

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Erro ao configurar a API do Google: {e}")

def formatar_imovel_para_ia(imovel):
    """
    Cria um dicionário com os dados formatados do imóvel para usar no prompt.
    """
    caracteristicas_list = []
    if imovel.lavabo: caracteristicas_list.append('Lavabo')
    if imovel.escritorio: caracteristicas_list.append('Escritório')
    if imovel.varanda: caracteristicas_list.append('Varanda/Sacada')
    if imovel.piscina_privativa: caracteristicas_list.append('Piscina Privativa')
    if imovel.churrasqueira_privativa: caracteristicas_list.append('Churrasqueira Privativa')
    if imovel.mobiliado: caracteristicas_list.append('Mobiliado')
    if imovel.ar_condicionado: caracteristicas_list.append('Ar Condicionado')
    if imovel.moveis_planejados: caracteristicas_list.append('Móveis Planejados')
    
    caracteristicas_str = ", ".join(caracteristicas_list) if caracteristicas_list else "Nenhuma característica especial informada."

    return {
        'titulo': imovel.titulo_anuncio or "Não informado",
        'tipo_imovel': imovel.get_tipo_display() or "Não informado",
        'finalidade': imovel.get_finalidade_display() or "Não informado",
        'bairro': imovel.bairro or "Não informado",
        'cidade': imovel.cidade or "Não informado",
        'valor_venda': f"R$ {imovel.valor_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if imovel.valor_venda else "A consultar",
        'valor_aluguel': f"R$ {imovel.valor_aluguel:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if imovel.valor_aluguel else "A consultar",
        'area_util': f"{imovel.area_util}m²" if imovel.area_util else "Não informada",
        'quartos': imovel.quartos or "Não informado",
        'suites': imovel.suites or "Não informado",
        'banheiros': imovel.banheiros or "Não informado",
        'vagas': imovel.vagas_garagem or "Não informado",
        'caracteristicas': caracteristicas_str,
        'descricao_completa': imovel.descricao_completa or "Consulte para mais detalhes."
    }

class GerarTextoPublicacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        imovel_id = request.data.get('imovel_id')
        if not imovel_id:
            return Response(
                {"error": "O ID do imóvel é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=request.tenant)
        except Imovel.DoesNotExist:
            return Response(
                {"error": "Imóvel não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            prompt_config = ModeloDePrompt.objects.get(em_uso=True)
            template_prompt = prompt_config.template_do_prompt
        except ModeloDePrompt.DoesNotExist:
            return Response(
                {"error": "Nenhum modelo de prompt está ativo. Fale com o administrador do sistema."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        imobiliaria = request.tenant
        instrucao_voz = ""
        if hasattr(imobiliaria, 'voz_da_marca_preferida') and imobiliaria.voz_da_marca_preferida:
            instrucao_voz = imobiliaria.voz_da_marca_preferida.instrucao_ia

        dados_imovel = formatar_imovel_para_ia(imovel)
        dados_imovel['instrucao_voz'] = instrucao_voz
        
        prompt_final = template_prompt
        for key, value in dados_imovel.items():
            placeholder = '{{' + key + '}}'
            prompt_final = prompt_final.replace(placeholder, str(value))
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt_final)
            texto_gerado = response.text

            return Response({"texto_sugerido": texto_gerado}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"DEBUG: Erro na API do Google Gemini: {e}")
            return Response(
                {"error": f"Erro ao comunicar com a API de IA: {e}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class PublicacaoRedeSocialView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        imovel_id = request.data.get('imovel_id')
        texto_da_publicacao = request.data.get('texto')
        plataformas = request.data.get('plataformas', [])
        
        try:
            imovel = Imovel.objects.get(id=imovel_id, imobiliaria=request.tenant)
        except Imovel.DoesNotExist:
            return Response({'error': 'Imóvel não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            post_agendado = PostAgendado.objects.create(
                imovel=imovel,
                imobiliaria=request.tenant,
                agendado_por=request.user.perfil,
                texto=texto_da_publicacao,
                plataformas=plataformas,
                data_agendamento=timezone.now(),
                status='AGENDADO'
            )
            
            publicar_post_agendado.delay(post_agendado.id)
            
            return Response(
                {"success": "Publicação enviada para processamento. Verifique o histórico em breve!"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": f"Erro ao agendar a publicação: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AgendarPublicacaoView(APIView):
    """
    Endpoint para agendar uma publicação para o futuro.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        imovel_id = request.data.get('imovel_id')
        texto = request.data.get('texto')
        plataformas = request.data.get('plataformas')
        data_agendamento_str = request.data.get('data_agendamento')

        if not all([imovel_id, texto, plataformas, data_agendamento_str]):
            return Response(
                {"error": "Todos os campos (imovel_id, texto, plataformas, data_agendamento) são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            naive_datetime = datetime.fromisoformat(data_agendamento_str)
            data_agendamento_aware = timezone.make_aware(naive_datetime)
        except (ValueError, TypeError):
            return Response({"error": "Formato de data_agendamento inválido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=request.tenant)
        except Imovel.DoesNotExist:
            return Response({"error": "Imóvel não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(request.user, 'perfil'):
              return Response({"error": "Utilizador sem perfil associado."}, status=status.HTTP_400_BAD_REQUEST)

        post_agendado = PostAgendado.objects.create(
            imovel=imovel,
            imobiliaria=request.tenant,
            agendado_por=request.user.perfil,
            texto=texto,
            plataformas=plataformas,
            data_agendamento=data_agendamento_aware,
            status='AGENDADO'
        )
        
        publicar_post_agendado.apply_async(args=[post_agendado.id], eta=data_agendamento_aware)

        return Response(
            {"success": f"Publicação para o imóvel '{imovel.titulo_anuncio}' agendada com sucesso para {data_agendamento_str}!"},
            status=status.HTTP_201_CREATED
        )
    
class CalendarioPublicacoesView(APIView):
    """
    Fornece os dados de posts agendados e passados para
    serem exibidos num calendário.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get('start')
        end_date_str = request.query_params.get('end')

        if not start_date_str or not end_date_str:
            return Response(
                {"error": "Os parâmetros 'start' e 'end' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        except ValueError:
            return Response({"error": "Formato de data inválido."}, status=status.HTTP_400_BAD_REQUEST)
        
        posts = PostAgendado.objects.filter(
            imobiliaria=request.tenant,
            data_agendamento__gte=start_date,
            data_agendamento__lt=end_date
        )
        
        serializer = PostAgendadoSerializer(posts, many=True)
        return Response(serializer.data)
    
class PostAgendadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerir os posts agendados (CRUD - Criar, Ler, Atualizar, Excluir).
    """
    serializer_class = PostAgendadoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PostAgendado.objects.filter(imobiliaria=self.request.tenant)
        
class ImovelViewSet(viewsets.ModelViewSet):
    """
    Este é um ViewSet de "placeholder" para que o roteador aninhado funcione.
    A API de Imóveis provavelmente existe em app_imoveis.views.py.
    """
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Imovel.objects.filter(imobiliaria=self.request.tenant)


class PublicacaoHistoricoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para visualizar o histórico de publicações de um imóvel.
    """
    serializer_class = PublicacaoHistoricoSerializer

    def get_queryset(self):
        imovel_id = self.kwargs['imovel_pk']
        return PublicacaoHistorico.objects.filter(imovel_id=imovel_id).order_by('-data_publicacao')
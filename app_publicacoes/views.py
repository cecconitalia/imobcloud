# C:\wamp64\www\imobcloud\app_publicacoes\views.py

import os
import time
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
from .tasks import publicar_post_agendado
from django.utils import timezone
from datetime import datetime

# NOTA: A configuração GLOBAL da API do Google é removida daqui.
# A chave será configurada DENTRO do método POST, lendo do modelo Imobiliaria.

def formatar_imovel_para_ia(imovel):
    """
    Formata os dados do imóvel para serem inseridos no prompt.
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
    
    caracteristicas_str = ", ".join(caracteristicas_list) if caracteristicas_list else "Consulte detalhes."
    
    valor_venda_fmt = f"R$ {imovel.valor_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if imovel.valor_venda else "Sob Consulta"
    valor_aluguel_fmt = f"R$ {imovel.valor_aluguel:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if imovel.valor_aluguel else "Sob Consulta"

    resumo_completo = (
        f"Tipo: {imovel.get_tipo_display() or 'Imóvel'}\n"
        f"Título: {imovel.titulo_anuncio or ''}\n"
        f"Localização: {imovel.bairro or ''}, {imovel.cidade or ''}\n"
        f"Preço Venda: {valor_venda_fmt}\n"
        f"Preço Aluguel: {valor_aluguel_fmt}\n"
        f"Detalhes: {imovel.quartos or 0} quartos, {imovel.suites or 0} suítes, {imovel.banheiros or 0} banheiros, {imovel.vagas_garagem or 0} vagas.\n"
        f"Área: {imovel.area_util or 0}m²\n"
        f"Destaques: {caracteristicas_str}\n"
        f"Descrição Adicional: {imovel.descricao_completa or ''}"
    )

    return {
        'titulo': imovel.titulo_anuncio or "Oportunidade",
        'tipo_imovel': imovel.get_tipo_display() or "Imóvel",
        'finalidade': imovel.get_finalidade_display() or "",
        'bairro': imovel.bairro or "",
        'cidade': imovel.cidade or "",
        'valor_venda': valor_venda_fmt,
        'valor_aluguel': valor_aluguel_fmt,
        'area_util': f"{imovel.area_util}m²" if imovel.area_util else "",
        'quartos': imovel.quartos or "0",
        'suites': imovel.suites or "0",
        'banheiros': imovel.banheiros or "0",
        'vagas': imovel.vagas_garagem or "0",
        'caracteristicas': caracteristicas_str,
        'descricao_completa': imovel.descricao_completa or "",
        'imovel_data': resumo_completo
    }

class GerarTextoPublicacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        imovel_id = request.data.get('imovel_id')
        if not imovel_id:
            return Response({"error": "O ID do imóvel é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=request.tenant)
        except Imovel.DoesNotExist:
            return Response({"error": "Imóvel não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # -------------------------------------------------------------------
        # BLOCO CRÍTICO: Configuração da Chave da IA lida do modelo Imobiliaria
        # -------------------------------------------------------------------
        imobiliaria_key = request.tenant.google_gemini_api_key
        
        if not imobiliaria_key:
             return Response(
                {"error": "Chave API Gemini não configurada. Contate o administrador."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        try:
            # Configura a chave API antes de tentar gerar
            genai.configure(api_key=imobiliaria_key)
        except Exception as e:
            return Response(
                {"error": f"Erro ao configurar a IA com a chave fornecida: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        # -------------------------------------------------------------------

        # 1. Obter Template (Prompt)
        prompt_config = ModeloDePrompt.objects.filter(em_uso_descricao=True).first()
        if prompt_config:
            template_prompt = prompt_config.template_do_prompt
        else:
            template_prompt = "Crie uma legenda para Instagram para este imóvel:\n{{imovel_data}}\nTom de voz: {{voz_da_marca}}"

        # 2. Obter Voz da Marca
        instrucao_voz = "Profissional e convidativo."
        if hasattr(request.tenant, 'voz_da_marca_preferida') and request.tenant.voz_da_marca_preferida:
            instrucao_voz = request.tenant.voz_da_marca_preferida.instrucao_ia

        # 3. Preparar Dados
        dados_imovel = formatar_imovel_para_ia(imovel)
        dados_imovel['instrucao_voz'] = instrucao_voz
        dados_imovel['voz_da_marca'] = instrucao_voz 
        
        prompt_final = template_prompt
        for key, value in dados_imovel.items():
            placeholder = '{{' + key + '}}'
            prompt_final = prompt_final.replace(placeholder, str(value))
        
        prompt_final += "\n\nIMPORTANTE: Responda APENAS com o texto da legenda."

        # 4. Chamar IA com SISTEMA DE RETRY (Resolve o erro 429)
        modelos_para_tentar = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro', 'gemini-pro']

        for nome_modelo in modelos_para_tentar:
            try:
                model = genai.GenerativeModel(nome_modelo)
                response = model.generate_content(prompt_final)
                
                texto_limpo = ""
                if response and hasattr(response, 'text'):
                    texto_limpo = response.text
                elif response and hasattr(response, 'parts'):
                     texto_limpo = response.parts[0].text
                
                texto_limpo = texto_limpo.replace("```html", "").replace("```", "").strip()
                return Response({"texto_sugerido": texto_limpo}, status=status.HTTP_200_OK)

            except Exception as e:
                erro_msg = str(e)
                if "429" in erro_msg or "quota" in erro_msg.lower():
                    time.sleep(3) 
                    continue 
                elif "404" in erro_msg:
                    continue
                else:
                    return Response({"error": f"Erro na IA: {erro_msg}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(
            {"error": f"O sistema de IA está sobrecarregado (cota do Google). Por favor, aguarde o contador terminar."}, 
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

class PublicacaoRedeSocialView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        return Response({"error": "Use o endpoint /api/v1/publicacoes/agendar/"}, status=status.HTTP_400_BAD_REQUEST)

class AgendarPublicacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        imovel_id = request.data.get('imovel_id')
        texto = request.data.get('texto')
        imagens_ids = request.data.get('imagens_ids', [])
        publicar_agora = request.data.get('publicar_agora', False)
        data_agendamento_str = request.data.get('data_agendamento')

        if not imovel_id or not texto:
            return Response({"error": "Campos obrigatórios: imovel_id e texto."}, status=status.HTTP_400_BAD_REQUEST)

        data_agendamento_aware = timezone.now()
        
        if not publicar_agora:
            if not data_agendamento_str:
                return Response({"error": "Se não for publicar agora, a data é obrigatória."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                naive_datetime = datetime.fromisoformat(data_agendamento_str)
                data_agendamento_aware = timezone.make_aware(naive_datetime)
            except (ValueError, TypeError):
                return Response({"error": "Formato de data inválido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            imovel = Imovel.objects.get(pk=imovel_id, imobiliaria=request.tenant)
        except Imovel.DoesNotExist:
            return Response({"error": "Imóvel não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        post_agendado = PostAgendado.objects.create(
            imovel=imovel,
            imobiliaria=request.tenant,
            agendado_por=request.user.perfil if hasattr(request.user, 'perfil') else None,
            texto=texto,
            plataformas=['instagram'],
            imagens_ids=imagens_ids,
            data_agendamento=data_agendamento_aware,
            status='PROCESSANDO' if publicar_agora else 'AGENDADO'
        )
        
        if publicar_agora:
            publicar_post_agendado.delay(post_agendado.id)
            msg_sucesso = "Publicação enviada para processamento imediato!"
        else:
            publicar_post_agendado.apply_async(args=[post_agendado.id], eta=data_agendamento_aware)
            msg_sucesso = "Agendamento realizado com sucesso!"

        return Response({"success": msg_sucesso}, status=status.HTTP_201_CREATED)
    
class CalendarioPublicacoesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        if not start or not end:
            return Response({"error": "Faltam parâmetros start e end"}, status=400)
        try:
            start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
        except ValueError:
            return Response({"error": "Data inválida"}, status=400)
        
        posts = PostAgendado.objects.filter(
            imobiliaria=request.tenant,
            data_agendamento__gte=start_date,
            data_agendamento__lt=end_date
        )
        serializer = PostAgendadoSerializer(posts, many=True)
        return Response(serializer.data)
    
class PostAgendadoViewSet(viewsets.ModelViewSet):
    serializer_class = PostAgendadoSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return PostAgendado.objects.filter(imobiliaria=self.request.tenant)
        
class ImovelViewSet(viewsets.ModelViewSet):
    queryset = Imovel.objects.all()
    serializer_class = ImovelSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Imovel.objects.filter(imobiliaria=self.request.tenant)

class PublicacaoHistoricoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PublicacaoHistoricoSerializer
    def get_queryset(self):
        imovel_id = self.kwargs['imovel_pk']
        return PublicacaoHistorico.objects.filter(imovel_id=imovel_id).order_by('-data_publicacao')
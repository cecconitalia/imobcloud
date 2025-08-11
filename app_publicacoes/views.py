# app_publicacoes/views.py

import os
import facebook
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app_imoveis.models import Imovel
from .models import PublicacaoSocial, PlataformaChoices # Adicione esta importação



# Configura a API do Google com a chave que está no nosso .env
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Erro ao configurar a API do Google: {e}")


class GerarTextoPublicacaoView(APIView):
    """
    Esta View recebe o ID de um imóvel, busca os seus dados
    e usa a IA do Google (Gemini) para gerar um texto de marketing.
    """
    def post(self, request, *args, **kwargs):
        imovel_id = request.data.get('imovel_id')
        if not imovel_id:
            return Response(
                {"error": "O ID do imóvel é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            imovel = Imovel.objects.get(id=imovel_id)
        except Imovel.DoesNotExist:
            return Response(
                {"error": "Imóvel não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        # --- Aqui está a magia: O Prompt para a IA ---
        # Construímos um texto bem detalhado para dizer à IA exatamente o que queremos.
        prompt = f"""
        Aja como um especialista em marketing imobiliário para redes sociais.
        Crie uma legenda curta e impactante para uma publicação no Instagram e Facebook sobre o seguinte imóvel:

        - Tipo de Imóvel: {imovel.get_tipo_display()}
        - Localização: {imovel.bairro}, {imovel.cidade}
        - Quartos: {imovel.quartos}
        - Suítes: {imovel.suites}
        - Vagas de Garagem: {imovel.vagas_garagem}
        - Área Total: {imovel.area_total} m²
        - Preço de Venda: R$ {imovel.valor_venda}
        - Destaques na Descrição: {imovel.descricao_completa}

        **Requisitos da Legenda:**
        1.  **Tom de Voz:** Entusiasmado, profissional e convidativo.
        2.  **Estrutura:** Comece com uma frase que chame a atenção. Destaque 2 ou 3 dos melhores atributos do imóvel. Termine com uma chamada para ação clara (Call to Action).
        3.  **Emojis:** Use 3 a 4 emojis que complementem o texto de forma elegante.
        4.  **Hashtags:** Inclua 5 hashtags relevantes no final, como #imoveis, #{imovel.cidade.replace(' ', '')}, #casapropria.
        """

        try:
            # Inicializa o modelo da IA e gera o conteúdo
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            texto_gerado = response.text
        except Exception as e:
            # Em caso de erro com a API da IA, devolvemos uma mensagem clara.
            return Response(
                {"error": f"Erro ao comunicar com a IA: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Retorna o texto gerado com sucesso para o frontend.
        return Response({"texto_sugerido": texto_gerado}, status=status.HTTP_200_OK)
    

class PublicarPostView(APIView):
    """
    VERSÃO DE DEPURAÇÃO: Publica UMA foto para isolar o problema.
    """
    def post(self, request, *args, **kwargs):
        imovel_id = request.data.get('imovel_id')
        plataforma = request.data.get('plataforma')
        texto = request.data.get('texto')

        if not all([imovel_id, plataforma, texto]):
            return Response({"error": "Dados incompletos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            imovel_obj = Imovel.objects.get(id=imovel_id)
        except Imovel.DoesNotExist:
            return Response({"error": "Imóvel não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        imagem_principal = imovel_obj.imagens.order_by('ordem').first()
        if not imagem_principal:
            return Response({"error": "Imóvel sem imagens."}, status=status.HTTP_400_BAD_REQUEST)

        sucesso_na_publicacao = False
        link_da_publicacao = None

        try:
            access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
            graph = facebook.GraphAPI(access_token)
            imagem_url = request.build_absolute_uri(imagem_principal.imagem.url)

            if plataforma == PlataformaChoices.FACEBOOK:
                page_id = os.getenv('FACEBOOK_PAGE_ID')
                # Lógica simplificada: publicar uma foto com legenda.
                post_result = graph.put_photo(
                    image=imagem_url,
                    message=texto,
                    album_path=f'{page_id}/photos'
                )
                post_id = post_result.get('post_id') or post_result.get('id')
                link_da_publicacao = f"https://www.facebook.com/{post_id}"
                sucesso_na_publicacao = True

            elif plataforma == PlataformaChoices.INSTAGRAM:
                ig_user_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
                container_result = graph.post(
                    path=f'{ig_user_id}/media',
                    params={'image_url': imagem_url, 'caption': texto}
                )
                creation_id = container_result['id']
                graph.post(path=f'{ig_user_id}/media_publish', params={'creation_id': creation_id})
                link_da_publicacao = "https://www.instagram.com/"
                sucesso_na_publicacao = True

        except Exception as e:
            print(f"ERRO DETALHADO AO PUBLICAR EM '{plataforma.upper()}': {e}")
            sucesso_na_publicacao = False

        if sucesso_na_publicacao:
            # ... (código para guardar no banco de dados) ...
            return Response({"message": f"Publicado com sucesso no {plataforma}!"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": f"Falha ao publicar no {plataforma}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
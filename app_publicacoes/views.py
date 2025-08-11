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
from .models import PublicacaoSocial 

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Erro ao configurar a API do Google: {e}")

class GerarTextoPublicacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        imovel_id = request.data.get('imovel_id')
        if not imovel_id:
            return Response({"error": "O ID do imóvel é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            imovel = Imovel.objects.get(id=imovel_id)
        except Imovel.DoesNotExist:
            return Response({"error": "Imóvel não encontrado."}, status=status.HTTP_404_NOT_FOUND)

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
        1. **Tom de Voz:** Entusiasmado, profissional e convidativo.
        2. **Estrutura:** Comece com uma frase que chame a atenção. Destaque 2 ou 3 dos melhores atributos do imóvel. Termine com uma chamada para ação clara (Call to Action).
        3. **Emojis:** Use 3 a 4 emojis que complementem o texto de forma elegante.
        4. **Hashtags:** Inclua 5 hashtags relevantes no final, como #imoveis, #{imovel.cidade.replace(' ', '')}, #casapropria.
        """
        try:
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            response = model.generate_content(prompt)
            texto_gerado = response.text
        except Exception as e:
            return Response({"error": f"Erro ao comunicar com a IA: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"texto_sugerido": texto_gerado}, status=status.HTTP_200_OK)


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

        resultados = {}
        for plataforma in plataformas:
            if plataforma == 'facebook':
                try:
                    self.publicar_facebook(imovel, texto_da_publicacao)
                    resultados['facebook'] = 'Publicado com sucesso'
                    PublicacaoSocial.objects.create(
                        imovel=imovel, 
                        texto_gerado=texto_da_publicacao, 
                        plataforma='facebook', 
                        sucesso=True, 
                        publicado_por=request.user.perfil
                    )
                except Exception as e:
                    resultados['facebook'] = f'Erro: {str(e)}'
                    PublicacaoSocial.objects.create(
                        imovel=imovel, 
                        texto_gerado=texto_da_publicacao, 
                        plataforma='facebook', 
                        sucesso=False, 
                        publicado_por=request.user.perfil
                    )

            elif plataforma == 'instagram':
                try:
                    self.publicar_instagram(imovel, texto_da_publicacao)
                    resultados['instagram'] = 'Publicado com sucesso'
                    PublicacaoSocial.objects.create(
                        imovel=imovel, 
                        texto_gerado=texto_da_publicacao, 
                        plataforma='instagram', 
                        sucesso=True, 
                        publicado_por=request.user.perfil
                    )
                except Exception as e:
                    resultados['instagram'] = f'Erro: {str(e)}'
                    PublicacaoSocial.objects.create(
                        imovel=imovel, 
                        texto_gerado=texto_da_publicacao, 
                        plataforma='instagram', 
                        sucesso=False, 
                        publicado_por=request.user.perfil
                    )

        return Response(resultados, status=status.HTTP_200_OK)

    def publicar_facebook(self, imovel, texto):
        imobiliaria = imovel.imobiliaria
        page_id = imobiliaria.facebook_page_id
        access_token = imobiliaria.facebook_page_access_token

        if not page_id or not access_token:
            raise Exception("Credenciais do Facebook não configuradas.")

        primeira_imagem = ImagemImovel.objects.filter(imovel=imovel).order_by('ordem').first()
        if not primeira_imagem:
            raise Exception("Imóvel não possui imagem para publicação.")
        
        # !! IMPORTANTE !! - Coloque a sua URL atual do ngrok aqui
        base_url = "https://ab0d84a59e25.ngrok-free.app"
        image_url = f"{base_url}{primeira_imagem.imagem.url}" 

        url = f'https://graph.facebook.com/v18.0/{page_id}/photos'
        params = { 'caption': texto, 'url': image_url, 'access_token': access_token }
        response = requests.post(url, params=params)
        response_data = response.json()

        if 'error' in response_data:
            raise Exception(response_data['error']['message'])
        
        return response_data

    def publicar_instagram(self, imovel, texto):
        imobiliaria = imovel.imobiliaria
        ig_user_id = imobiliaria.instagram_business_account_id
        access_token = imobiliaria.facebook_page_access_token

        if not ig_user_id or not access_token:
            raise Exception("Credenciais do Instagram não configuradas.")

        primeira_imagem = ImagemImovel.objects.filter(imovel=imovel).order_by('ordem').first()
        if not primeira_imagem:
            raise Exception("Imóvel não possui imagem para publicação.")

        # !! IMPORTANTE !! - Coloque a sua URL atual do ngrok aqui
        base_url = "https://ab0d84a59e25.ngrok-free.app"
        image_url = f"{base_url}{primeira_imagem.imagem.url}"

        url_media = f'https://graph.facebook.com/v18.0/{ig_user_id}/media'
        params_media = { 'image_url': image_url, 'caption': texto, 'access_token': access_token }
        response_media = requests.post(url_media, params=params_media)
        media_data = response_media.json()

        if 'error' in media_data:
            raise Exception(media_data['error']['message'])
        
        creation_id = media_data.get('id')
        if not creation_id:
            raise Exception(f"Falha ao obter ID de criação. Resposta da API: {media_data}")

        url_publish = f'https://graph.facebook.com/v18.0/{ig_user_id}/media_publish'
        params_publish = { 'creation_id': creation_id, 'access_token': access_token }
        response_publish = requests.post(url_publish, params=params_publish)
        publish_data = response_publish.json()

        if 'error' in publish_data:
            raise Exception(publish_data['error']['message'])

        return publish_data
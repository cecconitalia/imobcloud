# C:\wamp64\www\imobcloud\app_publicacoes\tasks.py

import requests
import os
from ImobCloud.celery import app
from .models import PostAgendado, PublicacaoHistorico, PublicacaoSocial
from app_imoveis.models import Imovel, ImagemImovel
from django.utils import timezone

def publicar_facebook_api(imovel, texto):
    imobiliaria = imovel.imobiliaria
    page_id = imobiliaria.facebook_page_id
    access_token = imobiliaria.facebook_page_access_token

    if not page_id or not access_token:
        raise Exception("Credenciais do Facebook não configuradas.")

    primeira_imagem = ImagemImovel.objects.filter(imovel=imovel).order_by('ordem').first()
    if not primeira_imagem:
        raise Exception("Imóvel não possui imagem para publicação.")
    
    base_url = "https://9ddacb56c314.ngrok-free.app"
    image_url = f"{base_url}{primeira_imagem.imagem.url}" 

    url = f'https://graph.facebook.com/v18.0/{page_id}/photos'
    params = { 'caption': texto, 'url': image_url, 'access_token': access_token }
    response = requests.post(url, params=params)
    response_data = response.json()

    if 'error' in response_data:
        raise Exception(response_data['error']['message'])
    
    return response_data

def publicar_instagram_api(imovel, texto):
    imobiliaria = imovel.imobiliaria
    ig_user_id = imobiliaria.instagram_business_account_id
    access_token = imobiliaria.facebook_page_access_token

    if not ig_user_id or not access_token:
        raise Exception("Credenciais do Instagram não configuradas.")

    primeira_imagem = ImagemImovel.objects.filter(imovel=imovel).order_by('ordem').first()
    if not primeira_imagem:
        raise Exception("Imóvel não possui imagem para publicação.")

    base_url = "https://9ddacb56c314.ngrok-free.app"
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

@app.task(bind=True)
def publicar_post_agendado(self, post_agendado_id):
    """
    Tarefa Celery para executar a publicação agendada.
    """
    try:
        post = PostAgendado.objects.get(pk=post_agendado_id)
    except PostAgendado.DoesNotExist:
        return f"Post agendado com ID {post_agendado_id} não encontrado."

    imovel = post.imovel
    resultados = {}

    for plataforma in post.plataformas:
        if plataforma == 'facebook':
            try:
                response_data = publicar_facebook_api(imovel, post.texto)
                resultados['facebook'] = 'Publicado com sucesso'
                PublicacaoHistorico.objects.create(
                    imovel=imovel, 
                    rede_social='Facebook',
                    link_publicacao=response_data.get('post_id') if response_data else None
                )
                if hasattr(post.agendado_por, 'user'):
                    PublicacaoSocial.objects.create(
                        imovel=imovel, 
                        texto_gerado=post.texto, 
                        plataforma='facebook', 
                        sucesso=True, 
                        publicado_por=post.agendado_por
                    )
            except Exception as e:
                resultados['facebook'] = f'Erro: {str(e)}'
                if hasattr(post.agendado_por, 'user'):
                    PublicacaoSocial.objects.create(
                        imovel=imovel, 
                        texto_gerado=post.texto, 
                        plataforma='facebook', 
                        sucesso=False, 
                        publicado_por=post.agendado_por
                    )
        elif plataforma == 'instagram':
            try:
                publish_data = publicar_instagram_api(imovel, post.texto)
                resultados['instagram'] = 'Publicado com sucesso'
                PublicacaoHistorico.objects.create(
                    imovel=imovel, 
                    rede_social='Instagram',
                    link_publicacao=publish_data.get('id') if publish_data else None
                )
                if hasattr(post.agendado_por, 'user'):
                    PublicacaoSocial.objects.create(
                        imovel=imovel, 
                        texto_gerado=post.texto, 
                        plataforma='instagram', 
                        sucesso=True, 
                        publicado_por=post.agendado_por
                    )
            except Exception as e:
                resultados['instagram'] = f'Erro: {str(e)}'
                if hasattr(post.agendado_por, 'user'):
                    PublicacaoSocial.objects.create(
                        imovel=imovel, 
                        texto_gerado=post.texto, 
                        plataforma='instagram', 
                        sucesso=False, 
                        publicado_por=post.agendado_por
                    )
    
    post.status = 'PUBLICADO'
    post.save()

    return resultados
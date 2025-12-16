# -*- coding: utf-8 -*-
import requests

class MetaSocialService:
    """
    Servico para gerenciar publicacoes na API Graph do Facebook/Instagram.
    Documentacao: https://developers.facebook.com/docs/instagram-api/guides/content-publishing
    """
    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(self, access_token, facebook_page_id=None, instagram_business_id=None):
        self.access_token = access_token
        self.facebook_page_id = facebook_page_id
        self.instagram_business_id = instagram_business_id

    def post_facebook_photo(self, image_url, caption):
        """
        Publica uma foto na Pagina do Facebook.
        """
        if not self.facebook_page_id:
            raise ValueError("ID da Pagina do Facebook nao configurado para esta imobiliaria.")

        url = f"{self.BASE_URL}/{self.facebook_page_id}/photos"
        params = {
            'url': image_url,
            'caption': caption,
            'access_token': self.access_token
        }
        
        # Timeout de 30s para evitar travamento se a API demorar
        response = requests.post(url, params=params, timeout=30)
        data = response.json()

        if 'error' in data:
            raise Exception(f"Erro Facebook API: {data['error'].get('message', 'Erro desconhecido')}")
        
        # Retorna o ID do post criado
        return data.get('post_id') or data.get('id')

    def post_instagram_photo(self, image_url, caption):
        """
        Publica uma foto no Instagram Business (Feed).
        Processo em duas etapas: 1. Criar Container, 2. Publicar Container.
        """
        if not self.instagram_business_id:
            raise ValueError("ID da conta Instagram Business nao configurado para esta imobiliaria.")

        # --- Passo 1: Criar Container de Media ---
        url_container = f"{self.BASE_URL}/{self.instagram_business_id}/media"
        params_container = {
            'image_url': image_url,
            'caption': caption,
            'access_token': self.access_token
        }
        
        resp_container = requests.post(url_container, params=params_container, timeout=30)
        data_container = resp_container.json()

        if 'error' in data_container:
            raise Exception(f"Erro Instagram (Container): {data_container['error'].get('message')}")
            
        creation_id = data_container.get('id')
        if not creation_id:
            raise Exception("Falha ao obter ID de criacao do container do Instagram.")

        # --- Passo 2: Publicar o Container ---
        url_publish = f"{self.BASE_URL}/{self.instagram_business_id}/media_publish"
        params_publish = {
            'creation_id': creation_id,
            'access_token': self.access_token
        }
        
        resp_publish = requests.post(url_publish, params=params_publish, timeout=30)
        data_publish = resp_publish.json()

        if 'error' in data_publish:
            raise Exception(f"Erro Instagram (Publicacao): {data_publish['error'].get('message')}")
            
        return data_publish.get('id')
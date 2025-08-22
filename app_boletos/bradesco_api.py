# C:\wamp64\www\ImobCloud\app_boletos\bradesco_api.py

import requests
import json
from django.conf import settings
from .models import ConfiguracaoBanco
from core.models import Imobiliaria
from django.core.cache import cache
from django.utils.dateparse import parse_datetime
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.files.storage import default_storage

class BradescoAPI:
    """
    Serviço para gerenciar a comunicação com a API de Cobrança do Bradesco.
    """
    BRADESCO_API_BASE_URL_SANDBOX = 'https://openapisandbox.prebanco.com.br'
    BRADESCO_API_BASE_URL_PRODUCAO = 'https://openapi.bradesco.com.br'
    TOKEN_URL = '/auth/server-mtls/v2/token'

    def __init__(self, imobiliaria: Imobiliaria):
        self.imobiliaria = imobiliaria
        try:
            self.config = ConfiguracaoBanco.objects.get(
                imobiliaria=imobiliaria,
                nome_banco='Bradesco'
            )
            
            if not self.config.certificado_file or not self.config.chave_privada_file:
                 raise ValueError("Arquivos de certificado e chave privada não configurados para o Bradesco.")
            
            # APENAS OBTEMOS OS CAMINHOS DOS ARQUIVOS, SEM LER O CONTEÚDO
            self.cert_path = default_storage.path(self.config.certificado_file.name)
            self.key_path = default_storage.path(self.config.chave_privada_file.name)

        except ConfiguracaoBanco.DoesNotExist:
            raise ValueError("Configuração do Bradesco não encontrada para esta imobiliária.")

    def _get_api_base_url(self):
        """ Retorna a URL base da API com base no ambiente de desenvolvimento. """
        if settings.DEBUG:
            return self.BRADESCO_API_BASE_URL_SANDBOX
        return self.BRADESCO_API_BASE_URL_PRODUCAO

    def _get_access_token(self):
        """
        Obtém o token de acesso da API, usando cache para evitar requisições repetidas.
        """
        cache_key = f'bradesco_token_{self.imobiliaria.id}'
        token_data = cache.get(cache_key)

        if token_data:
            token_expiry = token_data.get('expires_at')
            if token_expiry and parse_datetime(token_expiry) > timezone.now() + timedelta(minutes=5):
                return token_data.get('access_token')
            else:
                cache.delete(cache_key)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
        }
        
        url = self._get_api_base_url() + self.TOKEN_URL

        try:
            # CORREÇÃO: Passamos a tupla com os CAMINHOS dos arquivos para o parâmetro 'cert'.
            # A biblioteca 'requests' se encarrega de abrir e ler os arquivos da forma correta.
            response = requests.post(
                url, 
                data=data, 
                headers=headers,
                cert=(self.cert_path, self.key_path),
                verify=True
            )
            response.raise_for_status()
            response_data = response.json()
            
            access_token = response_data.get('access_token')
            expires_in = response_data.get('expires_in')

            if access_token and expires_in:
                expires_at = timezone.now() + timedelta(seconds=expires_in)
                cache.set(cache_key, {'access_token': access_token, 'expires_at': expires_at}, timeout=expires_in)
                return access_token

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição da API do Bradesco para obter o token: {e}")
            raise
        except json.JSONDecodeError:
            print("Erro de decodificação JSON na resposta do Bradesco.")
            raise
        
        raise ValueError("Falha ao obter o token de acesso da API do Bradesco.")

    def gerar_boleto(self, dados_boleto):
        """
        Método para gerar um boleto na API do Bradesco.
        """
        access_token = self._get_access_token()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
        }
        
        url = self._get_api_base_url() + '/path/para/gerar/boleto' # Lembre-se de substituir pelo endpoint real
        
        try:
            # A mesma correção é aplicada aqui
            response = requests.post(
                url,
                data=json.dumps(dados_boleto),
                headers=headers,
                cert=(self.cert_path, self.key_path),
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição da API do Bradesco para gerar boleto: {e}")
            raise
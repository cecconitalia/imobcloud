# C:\wamp64\www\ImobCloud\app_clientes\utils.py

from datetime import datetime, timedelta
import os
import pickle
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings
from django.core.files.storage import default_storage

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_DIR = os.path.join(settings.MEDIA_ROOT, 'google_credentials')

def agendar_tarefa_no_calendario(tarefa):
    """
    Agenda uma tarefa como um evento no Google Calendar do corretor responsável.
    """
    try:
        corretor = tarefa.responsavel
        
        # 1. Carregar o arquivo de credenciais do corretor
        if not corretor.perfil.google_json_file:
            print(f"AVISO: O corretor {corretor.first_name} não tem um arquivo de credenciais do Google. Agendamento ignorado.")
            return

        json_file_path = default_storage.path(corretor.perfil.google_json_file.name)

        # 2. Iniciar o fluxo OAuth para obter o token de acesso
        # Como o processo OAuth requer interação, este é um fluxo de exemplo.
        # Numa aplicação real, a autenticação seria feita de forma separada.
        flow = Flow.from_client_secrets_file(
            json_file_path,
            scopes=SCOPES,
            redirect_uri='oob' # Usar "out of band" para um fluxo sem servidor de frontend
        )
        # Note: Esta parte do código é uma simplificação. A autenticação completa requer um fluxo web.
        # Vamos assumir que um token já foi obtido e está guardado no perfil do utilizador.
        # Por enquanto, o código abaixo é apenas um exemplo.

        # 3. Criar o evento no Google Calendar
        credentials = Credentials(token='YOUR_ACCESS_TOKEN_HERE') # Substituir pelo token real
        service = build('calendar', 'v3', credentials=credentials)

        event = {
            'summary': f"Tarefa: {tarefa.descricao}",
            'description': f"Tarefa da oportunidade '{tarefa.oportunidade.titulo}'",
            'start': {
                'date': tarefa.data_conclusao.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'date': (tarefa.data_conclusao + timedelta(days=1)).isoformat(), # Exemplo de evento de 1 dia
                'timeZone': 'America/Sao_Paulo',
            },
            'attendees': [
                {'email': corretor.email},
            ],
        }

        service.events().insert(calendarId='primary', body=event).execute()
        print(f"Tarefa '{tarefa.descricao}' agendada no Google Calendar de {corretor.first_name}.")

    except Exception as e:
        print(f"Erro ao agendar tarefa no Google Calendar: {e}")
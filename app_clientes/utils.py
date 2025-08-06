# C:\wamp64\www\ImobCloud\app_clientes\utils.py

from datetime import datetime, timedelta
import os
import pickle
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings
from django.core.files.storage import default_storage
import json # NOVO: Importar json

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_DIR = os.path.join(settings.MEDIA_ROOT, 'google_credentials')


def get_google_calendar_service(perfil):
    """
    Cria e retorna um objeto de serviço da Google Calendar API, utilizando o token
    armazenado no perfil do utilizador. Se o token não existir, retorna None.
    """
    if not perfil.google_calendar_token:
        return None
    
    try:
        credentials_data = json.loads(perfil.google_calendar_token)
        credentials = Credentials(**credentials_data)
        
        # O flow precisa de ser criado para que o refresh do token funcione
        json_file_path = default_storage.path(perfil.google_json_file.name)
        flow = Flow.from_client_secrets_file(
            json_file_path,
            scopes=SCOPES,
            redirect_uri='oob'
        )
        # Associa as credenciais ao flow, permitindo o refresh automático
        flow.credentials = credentials
        
        # Se o token expirou, ele será renovado automaticamente se houver um refresh_token
        if credentials.expired and credentials.refresh_token:
            flow.refresh_token(credentials.refresh_token)
            # Guarda o novo token atualizado
            perfil.google_calendar_token = json.dumps({
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            })
            perfil.save()
            
        return build('calendar', 'v3', credentials=credentials)

    except Exception as e:
        print(f"Erro ao carregar o token do Google Calendar: {e}")
        return None


def agendar_tarefa_no_calendario(tarefa):
    """
    Agenda uma tarefa como um evento no Google Calendar do corretor responsável.
    """
    try:
        corretor = tarefa.responsavel
        
        if not (hasattr(corretor, 'perfil') and corretor.perfil.google_calendar_token):
            print(f"AVISO: O corretor {corretor.first_name} não tem uma conta do Google Calendar conectada. Agendamento ignorado.")
            return

        # ATUALIZADO: Usamos a nova função utilitária para obter o serviço
        service = get_google_calendar_service(corretor.perfil)
        if not service:
            print(f"AVISO: Não foi possível obter o serviço do Google Calendar para {corretor.first_name}. Agendamento ignorado.")
            return
            
        event = {
            'summary': f"Tarefa: {tarefa.descricao}",
            'description': f"Tarefa da oportunidade '{tarefa.oportunidade.titulo}'",
            'start': {
                'date': tarefa.data_conclusao.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'date': (tarefa.data_conclusao + timedelta(days=1)).isoformat(),
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
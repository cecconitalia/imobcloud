# core/tasks.py

from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@shared_task
def verificar_bloqueios_task():
    """
    Tarefa agendada (Celery Beat) que executa o comando de gestão
    para verificar vencimentos e bloquear imobiliárias inadimplentes.
    """
    logger.info("Iniciando tarefa automática de verificação de bloqueios...")
    try:
        # Chama o comando que criamos em core/management/commands/verificar_bloqueios.py
        call_command('verificar_bloqueios')
        logger.info("Tarefa de verificação de bloqueios concluída com sucesso.")
        return "Verificação concluída."
    except Exception as e:
        logger.error(f"Erro ao executar verificação de bloqueios: {str(e)}")
        return f"Erro: {str(e)}"
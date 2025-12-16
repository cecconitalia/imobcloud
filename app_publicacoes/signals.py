from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import schedule
from .models import PostAgendado
from django.utils import timezone

@receiver(post_save, sender=PostAgendado)
def agendar_tarefa_publicacao(sender, instance, created, **kwargs):
    """
    Sempre que um PostAgendado for criado ou atualizado com status 'AGENDADO',
    cria ou atualiza a tarefa no Django-Q.
    """
    if instance.status == 'AGENDADO' and instance.data_agendamento:
        
        # Verificação básica: se a data já passou, tenta executar em breve (ex: +1 min) 
        # ou mantém a data se for futura.
        run_date = instance.data_agendamento
        if run_date < timezone.now():
            run_date = timezone.now()

        # Agenda a execução usando o banco de dados (sem Redis)
        schedule(
            'app_publicacoes.tasks.executar_post_agendado', # Caminho da função
            instance.id,                                     # ID do post como argumento
            schedule_type='O',                               # 'O' = Once (Uma vez)
            next_run=run_date,                               # Quando rodar
            name=f'post_agendado_{instance.id}',             # Nome único para evitar duplicatas
            repeats=1
        )
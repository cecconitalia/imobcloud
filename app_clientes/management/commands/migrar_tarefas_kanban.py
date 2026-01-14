# backend/app_clientes/management/commands/migrar_tarefas_kanban.py

from django.core.management.base import BaseCommand
from app_clientes.models import Tarefa
from django.db.models import Q

class Command(BaseCommand):
    help = 'Migra tarefas antigas para o novo formato Kanban (define status e imobiliaria)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando migração de tarefas para o Kanban...")

        # 1. Sincronizar Status (Concluída -> status='concluida')
        # Tarefas marcadas como concluídas no checkbox antigo, mas que estão 'pendente' no novo select
        tarefas_concluidas = Tarefa.objects.filter(concluida=True).exclude(status='concluida')
        updated_status = tarefas_concluidas.update(status='concluida')
        self.stdout.write(self.style.SUCCESS(f'- Status atualizado: {updated_status} tarefas movidas para Concluída.'))

        # 2. Popular Imobiliária (Linkar ao Tenant)
        # Tarefas que não têm o campo imobiliaria preenchido (ficam invisíveis na API)
        tarefas_sem_tenant = Tarefa.objects.filter(imobiliaria__isnull=True)
        count_tenant = 0
        
        for t in tarefas_sem_tenant:
            salvou = False
            # Tenta pegar da oportunidade
            if t.oportunidade and t.oportunidade.imobiliaria:
                t.imobiliaria = t.oportunidade.imobiliaria
                salvou = True
            
            # Se não tiver oportunidade, tenta pegar do responsável (corretor)
            elif not salvou and t.responsavel:
                # Verifica se o user tem o atributo imobiliaria (depende do seu model de User)
                if hasattr(t.responsavel, 'imobiliaria') and t.responsavel.imobiliaria:
                    t.imobiliaria = t.responsavel.imobiliaria
                    salvou = True
                # Fallback: Tenta pelo PerfilUsuario se houver lógica reversa, 
                # mas geralmente o user customizado já tem.
            
            if salvou:
                t.save()
                count_tenant += 1
        
        self.stdout.write(self.style.SUCCESS(f'- Tenant vinculado: {count_tenant} tarefas recuperadas.'))
        self.stdout.write(self.style.SUCCESS('Migração concluída com sucesso!'))
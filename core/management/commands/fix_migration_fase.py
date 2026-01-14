# C:\wamp64\www\imobcloud\core\management\commands\fix_migration_fase.py

from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Limpa a coluna fase da tabela de oportunidades para permitir a migração para ForeignKey'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando limpeza da coluna 'fase'...")
        
        with connection.cursor() as cursor:
            # 1. Limpa a tabela principal
            try:
                cursor.execute("UPDATE app_clientes_oportunidade SET fase = NULL;")
                self.stdout.write(self.style.SUCCESS("Sucesso: Tabela 'app_clientes_oportunidade' atualizada (fase = NULL)."))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Aviso tabela principal: {e}"))

            # 2. Limpa a tabela de histórico (Simple History)
            try:
                cursor.execute("UPDATE app_clientes_historicaloportunidade SET fase = NULL;")
                self.stdout.write(self.style.SUCCESS("Sucesso: Tabela 'app_clientes_historicaloportunidade' atualizada (fase = NULL)."))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Aviso tabela histórico (pode não existir ainda): {e}"))

        self.stdout.write(self.style.SUCCESS("Concluído! Agora você pode rodar 'makemigrations' e 'migrate'."))
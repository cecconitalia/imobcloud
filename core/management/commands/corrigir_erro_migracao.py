# C:\wamp64\www\imobcloud\core\management\commands\corrigir_erro_migracao.py

from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Limpa a coluna fase da tabela de oportunidades para permitir a migração'

    def handle(self, *args, **kwargs):
        self.stdout.write("Tentando limpar a coluna 'fase' (definir como NULL)...")
        
        with connection.cursor() as cursor:
            # 1. Tenta limpar a tabela principal
            try:
                # Primeiro tentamos remover a constraint NOT NULL se existir (postgresql syntax)
                try:
                    cursor.execute("ALTER TABLE app_clientes_oportunidade ALTER COLUMN fase DROP NOT NULL;")
                except Exception:
                    pass # Se falhar, pode ser que já seja nullable ou outro DB

                cursor.execute("UPDATE app_clientes_oportunidade SET fase = NULL;")
                self.stdout.write(self.style.SUCCESS("SUCESSO: Coluna 'fase' limpa na tabela principal."))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Aviso tabela principal: {e}"))
                self.stdout.write(self.style.ERROR("Se o erro persistir, você precisará apagar as oportunidades antigas pelo banco ou shell."))

            # 2. Tenta limpar a tabela de histórico (se existir)
            try:
                try:
                    cursor.execute("ALTER TABLE app_clientes_historicaloportunidade ALTER COLUMN fase DROP NOT NULL;")
                except Exception:
                    pass

                cursor.execute("UPDATE app_clientes_historicaloportunidade SET fase = NULL;")
                self.stdout.write(self.style.SUCCESS("SUCESSO: Coluna 'fase' limpa no histórico."))
            except Exception as e:
                pass # Tabela pode não existir ainda

        self.stdout.write(self.style.SUCCESS("Processo concluído. Tente rodar 'makemigrations' e 'migrate' agora."))
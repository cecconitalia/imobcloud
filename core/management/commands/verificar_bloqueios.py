# core/management/commands/verificar_bloqueios.py

from django.core.management.base import BaseCommand
from core.models import Imobiliaria
from django.utils import timezone

class Command(BaseCommand):
    help = 'Verifica assinaturas vencidas e aplica bloqueios automáticos conforme regra do plano'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando verificação de bloqueios financeiros...")
        
        # Busca todas as imobiliárias que não estão canceladas
        # Inclui as 'GRATIS' para verificar se expirou os 7 dias
        imobiliarias_ativas = Imobiliaria.objects.exclude(status_financeiro='CANCELADO')
        
        count_bloqueados = 0
        count_pendentes = 0
        count_ativos = 0

        for imob in imobiliarias_ativas:
            status_anterior = imob.status_financeiro
            
            # Executa a lógica definida no models.py
            imob.verificar_status_bloqueio()
            
            # Verifica se houve mudança para logar
            if imob.status_financeiro == 'BLOQUEADO' and status_anterior != 'BLOQUEADO':
                count_bloqueados += 1
                self.stdout.write(self.style.WARNING(f"[BLOQUEADO] Imobiliária: {imob.nome}"))
            
            elif imob.status_financeiro == 'PENDENTE' and status_anterior != 'PENDENTE':
                count_pendentes += 1
                self.stdout.write(f"[PENDENTE] Imobiliária: {imob.nome} (Entrou no período de tolerância)")
                
            elif imob.status_financeiro == 'ATIVO':
                count_ativos += 1

        self.stdout.write(self.style.SUCCESS(
            f"Processo finalizado.\n"
            f"- Bloqueados hoje: {count_bloqueados}\n"
            f"- Tornaram-se Pendentes: {count_pendentes}\n"
            f"- Total Verificado: {imobiliarias_ativas.count()}"
        ))
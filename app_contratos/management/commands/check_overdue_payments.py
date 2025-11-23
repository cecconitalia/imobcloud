# C:\wamp64\www\imobcloud\app_contratos\management\commands\check_overdue_payments.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from app_contratos.models import Pagamento 
from app_financeiro.models import Transacao 
from django.db.models import Q

class Command(BaseCommand):
    help = 'Verifica pagamentos e transações pendentes e atualiza o status para ATRASADO.'

    def handle(self, *args, **kwargs):
        hoje = timezone.now().date()

        self.stdout.write(self.style.NOTICE(f'Iniciando verificação de pagamentos atrasados para a data {hoje}...'))

        # 1. Atualiza Pagamentos (ligados ao Contrato)
        pagamentos_a_atualizar = Pagamento.objects.filter(
            status='PENDENTE',
            data_vencimento__lt=hoje
        )
        pagamentos_atualizados = pagamentos_a_atualizar.update(status='ATRASADO')

        # 2. Atualiza Transações Receber/Pagar (RECEITA de aluguel e DESPESA de repasse)
        # Filtra por transações PENDENTES que venceram antes de hoje.
        # Condições: 
        # a) É uma Receita de Aluguel (ligada a contrato)
        # b) OU É uma Despesa de Repasse (ligada a transação_origem)
        transacoes_a_atualizar = Transacao.objects.filter(
            Q(tipo='RECEITA', contrato__tipo_contrato='ALUGUEL') | Q(transacao_origem__isnull=False),
            status='PENDENTE',
            data_vencimento__lt=hoje
        )
        transacoes_atualizadas = transacoes_a_atualizar.update(status='ATRASADO')

        self.stdout.write(self.style.SUCCESS(
            f'SUCESSO: {pagamentos_atualizados} registro(s) de Pagamento atualizado(s) para ATRASADO.'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'SUCESSO: {transacoes_atualizadas} registro(s) de Transação (Financeiro) atualizado(s) para ATRASADO.'
        ))
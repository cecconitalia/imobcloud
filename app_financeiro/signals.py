# C:\wamp64\www\imobcloud\app_financeiro\signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging
# Assumindo que Pagamento e Contrato estão disponíveis via app_contratos
from app_contratos.models import Pagamento, Contrato
from .models import Transacao # Transacao está neste app

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Transacao)
def sincronizar_pagamento_contrato(sender, instance, created, **kwargs):
    """
    Sincroniza o status do modelo Pagamento (em app_contratos) com o status
    da Transacao sempre que uma Transacao é salva.
    
    Isto é crucial para que o modal financeiro mostre o status PAGO.
    """
    
    # 1. Só processa se a transação estiver ligada a um Contrato
    if instance.contrato:
        
        # 2. Busca o Pagamento correspondente (Assumimos a correspondência
        #    pela chave Contrato + Valor + Data de Vencimento, o que é frágil
        #    mas necessário sem uma FK direta entre Pagamento e Transacao)
        try:
            # Filtramos pelo valor e data de vencimento para encontrar o Pagamento
            pagamento_contrato = Pagamento.objects.get(
                contrato=instance.contrato,
                valor=instance.valor,
                data_vencimento=instance.data_vencimento
            )
            
            status_novo = instance.status
            
            # 3. Sincronização
            if status_novo == 'PAGO' and pagamento_contrato.status != 'PAGO':
                # Transacao foi paga, atualizamos o Pagamento
                pagamento_contrato.status = 'PAGO'
                pagamento_contrato.data_pagamento = instance.data_pagamento or timezone.now().date()
                pagamento_contrato.save()
                logger.info(f"Financeiro: Sincronização OK. Pagamento Contrato {instance.contrato.id} atualizado para PAGO.")
                
            elif status_novo == 'CANCELADO' and pagamento_contrato.status not in ['PAGO', 'CANCELADO']:
                 # Transacao cancelada, atualiza o Pagamento
                pagamento_contrato.status = 'CANCELADO'
                pagamento_contrato.save()
            
        except Pagamento.DoesNotExist:
            # Isto pode ocorrer se a transação for a comissão de venda (que não tem Pagamento correspondente)
            # ou se a correspondência falhar.
            logger.debug(f"Sincronização: Pagamento correspondente não encontrado para Transacao {instance.id}.")
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
    """
    
    # 1. Só processa se a transação estiver ligada a um Contrato e for ALUGUEL
    if instance.contrato and instance.contrato.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
        
        try:
            # 2. CORREÇÃO CRÍTICA: Busca segura. 
            # Usa filter().first() em vez de get() para evitar 'MultipleObjectsReturned'
            # caso existam duas parcelas com o mesmo vencimento (acordos, erros antigos).
            pagamento_contrato = Pagamento.objects.filter(
                contrato=instance.contrato,
                data_vencimento=instance.data_vencimento
            ).first()
            
            if not pagamento_contrato:
                logger.warning(f"Sincronização: Nenhum Pagamento encontrado para Transacao {instance.id} (Venc: {instance.data_vencimento}).")
                return

            status_novo = instance.status
            
            # 3. Sincronização
            if status_novo == 'PAGO' and pagamento_contrato.status != 'PAGO':
                # Transacao foi paga, atualizamos o Pagamento
                pagamento_contrato.status = 'PAGO'
                pagamento_contrato.data_pagamento = instance.data_pagamento or timezone.now().date()
                pagamento_contrato.save()
                logger.info(f"Financeiro: Sincronização OK. Pagamento ID {pagamento_contrato.id} atualizado para PAGO.")
                
            elif status_novo in ['CANCELADO', 'RESCINDIDO'] and pagamento_contrato.status not in ['PAGO', 'CANCELADO']:
                 # Transacao cancelada/excluída, atualiza o Pagamento
                pagamento_contrato.status = 'CANCELADO'
                pagamento_contrato.save()
                logger.info(f"Financeiro: Pagamento ID {pagamento_contrato.id} marcado como CANCELADO via Transacao.")
            
        except Exception as e:
            logger.error(f"Sincronização ERRO CRÍTICO: Falha ao sincronizar Transacao {instance.id} -> {e}")
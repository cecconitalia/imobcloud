# C:\wamp64\www\ImobCloud\app_financeiro\signals.py

from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from .models import Transacao
from app_contratos.models import Pagamento
from datetime import date

@receiver(pre_save, sender=Transacao)
def sincronizar_pagamento_do_contrato(sender, instance, **kwargs):
    """
    Garante que, se uma Transacao de contrato for paga no financeiro, 
    o Pagamento original do contrato seja atualizado.
    """
    
    # 1. Só executa se a transação tiver um contrato vinculado
    if not instance.contrato:
        return

    # 2. Verifica se é uma edição (se tem 'pk')
    if instance.pk:
        try:
            obj_antigo = Transacao.objects.get(pk=instance.pk)
            status_antigo = obj_antigo.status
        except Transacao.DoesNotExist:
            return # Objeto antigo não existe, não faz nada
        
        status_novo = instance.status

        # 3. CONDIÇÃO PRINCIPAL:
        # Se o status mudou para PAGO (e não era PAGO antes)
        if status_novo == 'PAGO' and status_antigo != 'PAGO':
            
            # 4. Encontra o Pagamento correspondente no contrato
            try:
                pagamento_correspondente = Pagamento.objects.get(
                    contrato=instance.contrato,
                    data_vencimento=instance.data_vencimento, # Usa a data de vencimento como chave
                    status__in=['PENDENTE', 'ATRASADO']
                )
                
                # 5. Atualiza o Pagamento
                pagamento_correspondente.status = 'PAGO'
                pagamento_correspondente.data_pagamento = instance.data_pagamento or date.today()
                pagamento_correspondente.forma_pagamento_recebida = instance.forma_pagamento
                pagamento_correspondente.save()

            except Pagamento.DoesNotExist:
                # Transação paga, mas não encontrou Pagamento. Pode ser uma comissão de venda (manual).
                pass
            except Pagamento.MultipleObjectsReturned:
                 # ERRO: Múltiplos pagamentos encontrados. Logar isso futuramente.
                 pass


@receiver(pre_delete, sender=Transacao)
def reverter_pagamento_se_transacao_deletada(sender, instance, **kwargs):
    """
    Se uma Transação de contrato PAGA for DELETADA, o Pagamento
    correspondente deve voltar a ser PENDENTE para evitar inconsistência.
    """
    
    # 1. Só executa se a transação tiver um contrato vinculado
    if not instance.contrato:
        return

    # 2. Só executa se a transação deletada estava PAGA
    if instance.status != 'PAGO':
        return

    # 3. Encontra o Pagamento correspondente que estava PAGO
    try:
        pagamento_correspondente = Pagamento.objects.get(
            contrato=instance.contrato,
            data_vencimento=instance.data_vencimento,
            status='PAGO'
        )
        
        # 4. Reverte o Pagamento para PENDENTE
        pagamento_correspondente.status = 'PENDENTE'
        pagamento_correspondente.data_pagamento = None
        pagamento_correspondente.forma_pagamento_recebida = None
        pagamento_correspondente.save()

    except Pagamento.DoesNotExist:
        pass # Não encontrou pagamento pago, o que é normal.
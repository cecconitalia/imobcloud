# C:\wamp64\www\imobcloud\app_contratos\signals.py

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Contrato, Pagamento
from app_financeiro.models import Transacao, Categoria, Conta
from dateutil.relativedelta import relativedelta
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Contrato)
def gerenciar_financeiro_por_status(sender, instance, **kwargs):
    """
    NOTA: Este signal está desativado.
    A lógica de geração financeira foi movida para o ContratoCriacaoSerializer.
    """
    return # Desativa o signal


@receiver(pre_save, sender=Contrato)
def atualizar_datas_baseado_no_status(sender, instance, **kwargs):
    """
    Garante que as datas (início, assinatura) sejam preenchidas
    automaticamente se o contrato for ATIVADO sem elas.
    """
    if instance.pk: # Apenas em updates
        try:
            obj_anterior = sender.objects.get(pk=instance.pk)
            status_anterior = obj_anterior.status_contrato
            status_novo = instance.status_contrato

            if status_novo == Contrato.Status.ATIVO and status_anterior != Contrato.Status.ATIVO:
                if not instance.data_assinatura:
                    instance.data_assinatura = timezone.now().date()
                if not instance.data_inicio:
                    instance.data_inicio = instance.data_assinatura
                    
        except sender.DoesNotExist:
            pass 
            
    else:
        if instance.status_contrato == Contrato.Status.ATIVO:
            if not instance.data_assinatura:
                instance.data_assinatura = timezone.now().date()
            if not instance.data_inicio:
                instance.data_inicio = instance.data_assinatura


@receiver(pre_save, sender=Contrato)
def limpar_financeiro_se_cancelado(sender, instance, **kwargs):
    """
    Se o contrato for movido para RASCUNHO, CANCELADO ou RESCINDIDO,
    ele deve limpar quaisquer transações PENDENTES ou ATRASADAS para permitir regeneração.
    """
    if not instance.pk:
        return # Ação apenas para contratos existentes
        
    try:
        obj_anterior = sender.objects.get(pk=instance.pk)
        status_anterior = obj_anterior.status_contrato
        status_novo = instance.status_contrato
        
        # Status que disparam a limpeza
        novos_status_limpeza = [
            Contrato.Status.RESCINDIDO,
            Contrato.Status.CONCLUIDO,
            Contrato.Status.CANCELADO,
            Contrato.Status.RASCUNHO, 
        ]
        
        status_validos_anteriores = [
            Contrato.Status.RASCUNHO,
            Contrato.Status.ATIVO,
        ]
        
        # Se o status MUDOU de (Rascunho/Ativo) PARA (Limpeza)
        # OU se permaneceu em RASCUNHO (edição de rascunho)
        should_clean = (status_novo in novos_status_limpeza and status_anterior in status_validos_anteriores)
        
        if should_clean:
            
            # ==========================================================
            # === CORREÇÃO: Remove também ATRASADO, mantém PAGO      ===
            # ==========================================================
            # Removemos qualquer conta que não esteja efetivamente PAGA.
            # Isso resolve o problema de contas vencidas bloqueando a regeneração.
            
            transacoes_para_remover = Transacao.objects.filter(
                contrato=instance
            ).exclude(
                status__in=['PAGO', 'CONCILIADO'] 
            )
            # Nota: Se a sua Transacao não tiver 'CONCILIADO', o exclude funciona igual.
            # Alternativa explícita: status__in=['PENDENTE', 'ATRASADO']
            
            if transacoes_para_remover.exists():
                count = transacoes_para_remover.count()
                transacoes_para_remover.delete()
                logger.info(f"Signal: Contrato {instance.id} resetado/cancelado. {count} transações não-pagas foram removidas.")

            # Mesma lógica para Pagamentos (espelho)
            pagamentos_para_remover = Pagamento.objects.filter(
                contrato=instance
            ).exclude(
                status='PAGO'
            )
            
            if pagamentos_para_remover.exists():
                pagamentos_para_remover.delete()

    except sender.DoesNotExist:
        pass
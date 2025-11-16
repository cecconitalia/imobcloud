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
    A lógica de geração financeira foi movida para o ContratoCriacaoSerializer
    para lidar corretamente com o contexto da requisição 'ativar'.
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

            # Se o contrato está sendo ativado
            if status_novo == Contrato.Status.ATIVO and status_anterior != Contrato.Status.ATIVO:
                if not instance.data_assinatura:
                    instance.data_assinatura = timezone.now().date()
                if not instance.data_inicio:
                    instance.data_inicio = instance.data_assinatura
                    
        except sender.DoesNotExist:
            pass # Objeto novo, o form cuida disso
            
    # Se for um objeto novo (sem PK)
    else:
        if instance.status_contrato == Contrato.Status.ATIVO:
            if not instance.data_assinatura:
                instance.data_assinatura = timezone.now().date()
            if not instance.data_inicio:
                instance.data_inicio = instance.data_assinatura


@receiver(pre_save, sender=Contrato)
def limpar_financeiro_se_cancelado(sender, instance, **kwargs):
    """
    Se o contrato for movido para CANCELADO ou RESCINDIDO,
    ele deve limpar quaisquer transações PENDENTES futuras.
    """
    if not instance.pk:
        return # Ação apenas para contratos existentes
        
    try:
        obj_anterior = sender.objects.get(pk=instance.pk)
        status_anterior = obj_anterior.status_contrato
        status_novo = instance.status_contrato
        
        novos_status_cancelamento = [
            Contrato.Status.RESCINDIDO,
            Contrato.Status.CONCLUIDO,
            Contrato.Status.CANCELADO,
        ]
        
        status_validos_anteriores = [
            Contrato.Status.RASCUNHO,
            Contrato.Status.ATIVO,
        ]
        
        # Se o status MUDOU de (Rascunho ou Ativo) PARA (Cancelado, Rescindido, Concluido)
        if status_novo in novos_status_cancelamento and status_anterior in status_validos_anteriores:
            
            # ==========================================================
            # === CORREÇÃO: Usando string 'PENDENTE' para Transacao  ===
            # ==========================================================
            transacoes_pendentes = Transacao.objects.filter(
                contrato=instance,
                status='PENDENTE' # <-- CORRIGIDO
            )
            # ==========================================================
            
            if transacoes_pendentes.exists():
                count = transacoes_pendentes.count()
                transacoes_pendentes.delete()
                logger.info(f"Signal: Contrato {instance.id} movido para {status_novo}. {count} transações pendentes foram removidas.")

            # Deleta Pagamentos PENDENTES (do modelo antigo, se houver)
            pagamentos_pendentes = Pagamento.objects.filter(
                contrato=instance,
                status='PENDENTE'
            )
            if pagamentos_pendentes.exists():
                pagamentos_pendentes.delete()

    except sender.DoesNotExist:
        pass # Objeto novo
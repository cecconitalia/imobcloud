# C:\wamp64\www\ImobCloud\app_contratos\signals.py

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import Contrato, Pagamento
from app_financeiro.models import Transacao
from datetime import date
from django.db import transaction

# ==================================================================
# Lógica de Geração Automática (pre_save)
# Dispara quando o contrato é salvo, ANTES de ir para o banco.
# ESTA É A FONTE ÚNICA DA VERDADE PARA GATILHOS DE STATUS.
# ==================================================================

@receiver(pre_save, sender=Contrato)
@transaction.atomic
def disparar_gatilhos_financeiros_por_status(sender, instance, **kwargs):
    
    # Se 'pk' não existe, é um novo contrato.
    if not instance.pk:
        # Se for criado já como ATIVO (o que o form permite)
        if instance.status_contrato == Contrato.Status.ATIVO:
            # O contrato ainda não foi salvo, então não podemos
            # chamar os métodos de instância que criam transações (eles precisam do ID).
            # Vamos adiar isso para um post_save.
            pass
        return # Sai do pre_save para novos contratos

    # É uma edição (pk existe). Precisamos do status antigo.
    try:
        obj_antigo = Contrato.objects.get(pk=instance.pk)
        status_antigo = obj_antigo.status_contrato
    except Contrato.DoesNotExist:
        return # Objeto antigo não existe, não faz nada
    
    status_novo = instance.status_contrato

    # CONDIÇÃO PRINCIPAL:
    # Só executa se o status MUDOU para ATIVO/CONCLUÍDO e ANTES não era.
    is_being_activated = (
        status_novo in [Contrato.Status.ATIVO, Contrato.Status.CONCLUIDO] and
        status_antigo not in [Contrato.Status.ATIVO, Contrato.Status.CONCLUIDO]
    )

    if not is_being_activated:
        return # Nenhuma mudança de status relevante

    # --- Gatilho de Aluguel ---
    if instance.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
        # Verifica se o financeiro já existe
        if not instance.pagamentos.exists():
            print(f"SIGNAL pre_save: Ativando contrato de ALUGUEL {instance.pk}. Gerando financeiro...")
            # Não podemos chamar instance.gerar_financeiro_aluguel() aqui
            # porque ele CRIA objetos (Pagamento, Transacao).
            # A instância ainda não foi salva (é pre_save).
            # Adiaremos para post_save.
            instance._gerar_financeiro_aluguel_post_save = True 
        else:
            print(f"SIGNAL pre_save: Contrato de ALUGUEL {instance.pk} ativado, mas financeiro já existe.")
    
    # --- Gatilho de Venda (CORRIGIDO) ---
    elif instance.tipo_contrato == Contrato.TipoContrato.VENDA:
        # Verifica se a transação já existe
        if not Transacao.objects.filter(contrato=instance, tipo='RECEITA').exists():
            print(f"SIGNAL pre_save: Ativando contrato de VENDA {instance.pk}. Gerando comissão...")
            # Adiaremos para post_save
            instance._criar_comissao_venda_post_save = True
        else:
             print(f"SIGNAL pre_save: Contrato de VENDA {instance.pk} ativado, mas comissão já existe.")


# ==================================================================
# Lógica de Geração Automática (post_save)
# Executa DEPOIS que o contrato foi salvo, usando as flags
# que definimos no pre_save.
# ==================================================================

@receiver(post_save, sender=Contrato)
@transaction.atomic
def executar_gatilhos_financeiros_post_save(sender, instance, created, **kwargs):
    
    # Se foi criado já como ATIVO
    if created and instance.status_contrato == Contrato.Status.ATIVO:
        if instance.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
            print(f"SIGNAL post_save (CREATE): Contrato de ALUGUEL {instance.pk} criado ATIVO. Gerando financeiro...")
            instance.gerar_financeiro_aluguel()
        elif instance.tipo_contrato == Contrato.TipoContrato.VENDA:
            print(f"SIGNAL post_save (CREATE): Contrato de VENDA {instance.pk} criado ATIVO. Gerando comissão...")
            instance.criar_transacao_comissao()
        return

    # Se foi ATUALIZADO (lógica vinda do pre_save)
    if hasattr(instance, '_gerar_financeiro_aluguel_post_save') and instance._gerar_financeiro_aluguel_post_save:
        print(f"SIGNAL post_save (UPDATE): Contrato de ALUGUEL {instance.pk} ATIVADO. Gerando financeiro...")
        instance.gerar_financeiro_aluguel()
        # Limpa a flag para evitar re-execução
        delattr(instance, '_gerar_financeiro_aluguel_post_save') 
    
    if hasattr(instance, '_criar_comissao_venda_post_save') and instance._criar_comissao_venda_post_save:
        print(f"SIGNAL post_save (UPDATE): Contrato de VENDA {instance.pk} ATIVADO. Gerando comissão...")
        instance.criar_transacao_comissao()
        # Limpa a flag para evitar re-execução
        delattr(instance, '_criar_comissao_venda_post_save')


@receiver(post_save, sender=Pagamento)
def atualizar_status_transacao(sender, instance, **kwargs):
    # Se um pagamento for marcado como PAGO, atualiza a transação correspondente
    if instance.status == 'PAGO':
        Transacao.objects.filter(
            contrato=instance.contrato, 
            data_vencimento=instance.data_vencimento,
            status__in=['PENDENTE', 'ATRASADO']
        ).update(
            status='PAGO',
            data_pagamento=instance.data_pagamento or date.today()
        )

@receiver(pre_delete, sender=Contrato)
def deletar_transacoes_pendentes(sender, instance, **kwargs):
    # Ao deletar um contrato, remove as transações PENDENTES associadas
    Transacao.objects.filter(contrato=instance, status='PENDENTE').delete()
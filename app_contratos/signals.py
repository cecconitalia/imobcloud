# C:\wamp64\www\ImobCloud\app_contratos\signals.py

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import Contrato, Pagamento
from app_financeiro.models import Transacao, Categoria, Conta
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import transaction

# ==================================================================
# Lógica de Geração e Limpeza Automática (pre_save)
# CORRIGIDO: Renomeado para gerenciar todos os estados
# ==================================================================

@receiver(pre_save, sender=Contrato)
@transaction.atomic
def gerenciar_financeiro_por_status(sender, instance, **kwargs):
    
    # 1. Só executa se for um contrato de ALUGUEL
    if instance.tipo_contrato != Contrato.TipoContrato.ALUGUEL:
        return

    # 2. Verifica se o contrato está sendo EDITADO
    if instance.pk: # Se 'pk' existe, o contrato já está no banco (é uma edição)
        try:
            obj_antigo = Contrato.objects.get(pk=instance.pk)
            status_antigo = obj_antigo.status_contrato
        except Contrato.DoesNotExist:
            return # Objeto antigo não existe, não faz nada
            
        status_novo = instance.status_contrato

        # Se o status não mudou, não faz nada
        if status_novo == status_antigo:
            return

        # -----------------------------------------------------
        # CASO 1: CONTRATO ESTÁ SENDO ATIVADO (Lógica Original)
        # -----------------------------------------------------
        # Só gera se o status MUDOU para ATIVO e ANTES não era ATIVO
        if status_novo == Contrato.Status.ATIVO and status_antigo != Contrato.Status.ATIVO:
            
            # 4. Verifica se o financeiro já existe (para evitar duplicidade)
            if Pagamento.objects.filter(contrato=instance).exists():
                print(f"Contrato {instance.pk} já possui financeiro. Ativação normal.")
                return # Financeiro já existe, não faz nada.

            # 5. Validação dos dados
            if not instance.aluguel or not instance.duracao_meses or not instance.data_inicio:
                print(f"ERRO NO SIGNAL: Contrato {instance.pk} ativado sem valor, duração ou data de início.")
                # NOTA: Idealmente, isso deveria lançar uma exceção para a View.
                return 

            print(f"SIGNAL pre_save: Ativando contrato {instance.pk} e gerando financeiro...")
            
            # 6. GERAÇÃO DO FINANCEIRO
            # USA data_primeiro_vencimento se existir, senão usa data_inicio
            data_parcela = instance.data_primeiro_vencimento if instance.data_primeiro_vencimento else instance.data_inicio
            
            try:
                categoria_aluguel = Categoria.objects.get(imobiliaria=instance.imobiliaria, nome='Receita de Aluguel')
            except Categoria.DoesNotExist:
                categoria_aluguel = Categoria.objects.create(imobiliaria=instance.imobiliaria, nome='Receita de Aluguel', tipo='RECEITA')
                
            try:
                conta_padrao = Conta.objects.filter(imobiliaria=instance.imobiliaria).first()
            except Conta.DoesNotExist:
                conta_padrao = None

            duracao = instance.duracao_meses
            
            pagamentos_para_criar = []
            transacoes_para_criar = []

            for i in range(duracao):
                pagamento = Pagamento(
                    contrato=instance,
                    data_vencimento=data_parcela,
                    valor=instance.aluguel, 
                    status='PENDENTE'
                )
                pagamentos_para_criar.append(pagamento)
                
                transacao = Transacao(
                    imobiliaria=instance.imobiliaria,
                    descricao=f'Aluguel {i+1}/{duracao} - Imóvel: {instance.imovel.titulo_anuncio}',
                    valor=instance.aluguel,
                    data_transacao=date.today(), 
                    data_vencimento=data_parcela,
                    tipo='RECEITA',
                    status='PENDENTE',
                    categoria=categoria_aluguel,
                    conta=conta_padrao,
                    cliente=instance.inquilino,
                    imovel=instance.imovel,
                    contrato=instance
                )
                transacoes_para_criar.append(transacao)
                
                # Incrementa o mês para a próxima parcela
                data_parcela += relativedelta(months=1)
            
            Pagamento.objects.bulk_create(pagamentos_para_criar)
            Transacao.objects.bulk_create(transacoes_para_criar)
            print(f"SIGNAL: Financeiro ({len(pagamentos_para_criar)} parcelas) gerado para o contrato {instance.pk}.")

        # -----------------------------------------------------
        # CASO 2: CONTRATO ESTÁ SENDO DESATIVADO (Nova Lógica)
        # -----------------------------------------------------
        # Se o status ANTERIOR era ATIVO e o NOVO é um status de finalização
        status_finalizacao = [
            Contrato.Status.INATIVO, 
            Contrato.Status.RESCINDIDO, 
            Contrato.Status.CONCLUIDO
        ]
        
        if status_antigo == Contrato.Status.ATIVO and status_novo in status_finalizacao:
            print(f"SIGNAL pre_save: Desativando contrato {instance.pk}. Removendo financeiro pendente...")

            # Deleta todos os pagamentos PENDENTES
            pagamentos_deletados = Pagamento.objects.filter(
                contrato=instance, 
                status='PENDENTE'
            ).delete()
            
            # Deleta todas as transações PENDENTES
            transacoes_deletadas = Transacao.objects.filter(
                contrato=instance, 
                status='PENDENTE'
            ).delete()
            
            print(f"SIGNAL: {pagamentos_deletados[0] if pagamentos_deletados else 0} pagamentos e {transacoes_deletadas[0] if transacoes_deletadas else 0} transações pendentes removidas.")


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
            data_transacao=instance.data_pagamento or date.today(),
            forma_pagamento=instance.forma_pagamento_recebida
        )

@receiver(pre_delete, sender=Contrato)
def deletar_transacoes_pendentes(sender, instance, **kwargs):
    # Ao deletar um contrato, remove as transações PENDENTES associadas
    print(f"SIGNAL pre_delete: Deletando contrato {instance.pk}. Removendo financeiro pendente...")
    Transacao.objects.filter(contrato=instance, status='PENDENTE').delete()
    Pagamento.objects.filter(contrato=instance, status='PENDENTE').delete()
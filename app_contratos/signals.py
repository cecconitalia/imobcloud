# C:\wamp64\www\ImobCloud\app_contratos\signals.py

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from .models import Contrato, Pagamento
from app_financeiro.models import Transacao, Categoria, Conta
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import transaction

# ==================================================================
# Lógica de Geração Automática (pre_save)
# Dispara quando o contrato é salvo, ANTES de ir para o banco.
# ==================================================================

@receiver(pre_save, sender=Contrato)
@transaction.atomic
def gerar_financeiro_ao_ativar(sender, instance, **kwargs):
    
    # 1. Só executa se for um contrato de ALUGUEL
    if instance.tipo_contrato != Contrato.TipoContrato.ALUGUEL:
        return

    # 2. Verifica se o contrato está sendo ATIVADO
    if instance.pk: # Se 'pk' existe, o contrato já está no banco (é uma edição)
        try:
            obj_antigo = Contrato.objects.get(pk=instance.pk)
            status_antigo = obj_antigo.status_contrato
        except Contrato.DoesNotExist:
            return # Objeto antigo não existe, não faz nada
            
        status_novo = instance.status_contrato

        # 3. CONDIÇÃO PRINCIPAL:
        # Só gera se o status MUDOU para ATIVO e ANTES não era ATIVO
        if status_novo == Contrato.Status.ATIVO and status_antigo != Contrato.Status.ATIVO:
            
            # 4. Verifica se o financeiro já existe (para evitar duplicidade)
            if Pagamento.objects.filter(contrato=instance).exists():
                print(f"Contrato {instance.pk} já possui financeiro. Ativação normal.")
                return # Financeiro já existe, não faz nada.

            # 5. Validação dos dados (já foi feita na View, mas é uma segurança)
            if not instance.aluguel or not instance.duracao_meses:
                print(f"ERRO NO SIGNAL: Contrato {instance.pk} ativado sem valor/duração.")
                return 

            print(f"SIGNAL pre_save: Ativando contrato {instance.pk} e gerando financeiro...")
            
            # 6. GERAÇÃO DO FINANCEIRO
            data_parcela = instance.data_inicio
            
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
                
                data_parcela += relativedelta(months=1)
            
            Pagamento.objects.bulk_create(pagamentos_para_criar)
            Transacao.objects.bulk_create(transacoes_para_criar)
            print(f"SIGNAL: Financeiro ({len(pagamentos_para_criar)} parcelas) gerado para o contrato {instance.pk}.")


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
            data_transacao=instance.data_pagamento or date.today()
        )

@receiver(pre_delete, sender=Contrato)
def deletar_transacoes_pendentes(sender, instance, **kwargs):
    # Ao deletar um contrato, remove as transações PENDENTES associadas
    Transacao.objects.filter(contrato=instance, status='PENDENTE').delete()
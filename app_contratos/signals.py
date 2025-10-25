# C:\wamp64\www\ImobCloud\app_contratos\signals.py

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Contrato, Pagamento
from app_financeiro.models import Transacao, Categoria, Conta
from datetime import date
from dateutil.relativedelta import relativedelta

@receiver(post_save, sender=Contrato)
def criar_pagamentos_e_transacoes(sender, instance, created, **kwargs):
    # CORREÇÃO: Usando 'tipo_contrato' em vez de 'tipo'
    if created and instance.tipo_contrato == 'ALUGUEL':
        # Definir a data inicial para a primeira parcela
        data_parcela = instance.data_inicio
        
        # Obter ou criar categorias
        try:
            categoria_aluguel = Categoria.objects.get(imobiliaria=instance.imobiliaria, nome='Receita de Aluguel')
        except Categoria.DoesNotExist:
            categoria_aluguel = Categoria.objects.create(imobiliaria=instance.imobiliaria, nome='Receita de Aluguel', tipo='RECEITA')
            
        try:
            conta_padrao = Conta.objects.filter(imobiliaria=instance.imobiliaria).first()
        except Conta.DoesNotExist:
            conta_padrao = None

        # Usa a duração em meses (prazo) do contrato
        duracao = instance.duracao_meses or 12 # Fallback para 12 meses se não for definido

        for i in range(duracao):
            # Criar Pagamento
            pagamento = Pagamento.objects.create(
                contrato=instance,
                data_vencimento=data_parcela,
                valor=instance.valor_total, # Usando valor_total do contrato
                status='PENDENTE'
            )
            
            # Criar Transação correspondente
            Transacao.objects.create(
                imobiliaria=instance.imobiliaria,
                descricao=f'Aluguel {i+1}/{duracao} - Imóvel Cód: {instance.imovel.codigo_referencia}',
                valor=instance.valor_total,
                data_transacao=date.today(), 
                data_vencimento=data_parcela,
                tipo='RECEITA',
                status='PENDENTE',
                categoria=categoria_aluguel,
                conta=conta_padrao,
                cliente=instance.inquilino, # Usando o campo 'inquilino'
                imovel=instance.imovel,
                contrato=instance
            )
            
            # Adicionar um mês para a próxima parcela
            data_parcela += relativedelta(months=1)

@receiver(post_save, sender=Pagamento)
def atualizar_status_transacao(sender, instance, **kwargs):
    # Se um pagamento for marcado como PAGO, atualiza la transação correspondente
    if instance.status == 'PAGO':
        Transacao.objects.filter(contrato=instance.contrato, data_vencimento=instance.data_vencimento).update(
            status='PAGO',
            data_transacao=date.today()
        )

@receiver(pre_delete, sender=Contrato)
def deletar_transacoes_pendentes(sender, instance, **kwargs):
    # Ao deletar um contrato, remove as transações PENDENTES associadas
    Transacao.objects.filter(contrato=instance, status='PENDENTE').delete()
# C:\wamp64\www\ImobCloud\app_contratos\signals.py

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Contrato, Pagamento
from app_financeiro.models import Transacao, Categoria, Conta
from datetime import date
from dateutil.relativedelta import relativedelta

@receiver(post_save, sender=Contrato)
def criar_pagamentos_e_transacoes(sender, instance, created, **kwargs):
    
    # CORREÇÃO: Verificando usando a constante (TextChoice) do modelo
    if created and instance.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
        # Garantir que temos os dados necessários para aluguel
        if not instance.aluguel or not instance.duracao_meses:
            # Não deve acontecer se o serializer estiver correto, mas é uma segurança.
            return 

        data_parcela = instance.data_inicio
        
        # Obter ou criar categorias
        try:
            categoria_aluguel = Categoria.objects.get(imobiliaria=instance.imobiliaria, nome='Receita de Aluguel')
        except Categoria.DoesNotExist:
            categoria_aluguel = Categoria.objects.create(imobiliaria=instance.imobiliaria, nome='Receita de Aluguel', tipo='RECEITA')
            
        try:
            # CORREÇÃO: Garantir que a conta exista antes de usar
            conta_padrao = Conta.objects.filter(imobiliaria=instance.imobiliaria).first()
        except Conta.DoesNotExist:
            conta_padrao = None

        duracao = instance.duracao_meses # Já validado pelo serializer

        for i in range(duracao):
            # Criar Pagamento
            pagamento = Pagamento.objects.create(
                contrato=instance,
                data_vencimento=data_parcela,
                # CORREÇÃO CRÍTICA: Usando 'instance.aluguel' (valor mensal)
                valor=instance.aluguel, 
                status='PENDENTE'
            )
            
            # Criar Transação correspondente
            Transacao.objects.create(
                imobiliaria=instance.imobiliaria,
                descricao=f'Aluguel {i+1}/{duracao} - Imóvel Cód: {instance.imovel.codigo_referencia}',
                # CORREÇÃO CRÍTICA: Usando 'instance.aluguel' (valor mensal)
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
            
            # Adicionar um mês para a próxima parcela
            data_parcela += relativedelta(months=1)

@receiver(post_save, sender=Pagamento)
def atualizar_status_transacao(sender, instance, **kwargs):
    # Se um pagamento for marcado como PAGO, atualiza a transação correspondente
    if instance.status == 'PAGO':
        # CORREÇÃO: Garantindo que o status PAGO seja o valor UPPERCASE
        Transacao.objects.filter(
            contrato=instance.contrato, 
            data_vencimento=instance.data_vencimento,
            status__in=['PENDENTE', 'ATRASADO'] # Apenas atualiza se não estiver PAGO
        ).update(
            status='PAGO',
            data_transacao=instance.data_pagamento or date.today() # Usa a data do pagamento se houver
        )

@receiver(pre_delete, sender=Contrato)
def deletar_transacoes_pendentes(sender, instance, **kwargs):
    # Ao deletar um contrato, remove as transações PENDENTES associadas
    Transacao.objects.filter(contrato=instance, status='PENDENTE').delete()
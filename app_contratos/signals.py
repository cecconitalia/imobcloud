# app_contratos/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Contrato
from app_financeiro.models import Transacao, Categoria, ContaBancaria
from dateutil.relativedelta import relativedelta

@receiver(post_save, sender=Contrato)
def criar_contas_a_receber_aluguel(sender, instance, created, **kwargs):
    """
    Cria automaticamente as transações (contas a receber) para um novo
    contrato de aluguel ativo.
    """
    if created and instance.tipo_contrato == 'Aluguel' and instance.status_contrato == 'Ativo':

        # Encontra ou cria uma categoria padrão para aluguéis
        categoria_aluguel, _ = Categoria.objects.get_or_create(
            nome='Receita de Aluguel',
            imobiliaria=instance.imobiliaria,
            defaults={'tipo': 'RECEITA'}
        )
        
        # Tenta encontrar uma conta bancária padrão, ou usa a primeira que encontrar
        conta_bancaria = ContaBancaria.objects.filter(imobiliaria=instance.imobiliaria, ativo=True).first()
        if not conta_bancaria:
            # Se não houver conta bancária, a automação não pode continuar.
            # Pode-se criar uma notificação para o admin aqui.
            print(f"AVISO: Nenhuma conta bancária ativa encontrada para {instance.imobiliaria.nome}. As transações não foram criadas.")
            return

        valor_parcela = instance.valor_total # Assumindo que valor_total é o valor mensal
        data_inicio = instance.data_inicio

        # Gera uma transação para cada mês do contrato
        for i in range(instance.duracao_meses):
            data_vencimento = data_inicio + relativedelta(months=i)

            Transacao.objects.create(
                imobiliaria=instance.imobiliaria,
                tipo='RECEITA',
                descricao=f"Aluguel Ref: {instance.imovel.codigo_referencia} - Parcela {i+1}/{instance.duracao_meses}",
                valor=valor_parcela,
                data_vencimento=data_vencimento,
                status='PENDENTE',
                imovel=instance.imovel,
                contrato=instance,
                categoria=categoria_aluguel,
                conta_bancaria=conta_bancaria
            )
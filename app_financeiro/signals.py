# C:\wamp64\www\imobcloud\app_financeiro\signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging

# Importação do modelo principal (Imobiliaria)
from core.models import Imobiliaria

# Importações dos modelos do App Financeiro e Contratos
from app_contratos.models import Pagamento, Contrato
from .models import Transacao, Conta, FormaPagamento, Categoria

logger = logging.getLogger(__name__)

# ==============================================================================
# 1. SINAL DE SINCRONIZAÇÃO (Transação -> Pagamento de Aluguel)
# ==============================================================================
@receiver(post_save, sender=Transacao)
def sincronizar_pagamento_contrato(sender, instance, created, **kwargs):
    """
    Mantém o status do Pagamento (Contrato) igual ao da Transação Financeira.
    """
    if instance.contrato and instance.contrato.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
        try:
            pagamento_contrato = Pagamento.objects.filter(
                contrato=instance.contrato,
                data_vencimento=instance.data_vencimento
            ).first()
            
            if not pagamento_contrato:
                return

            status_novo = instance.status
            
            if status_novo == 'PAGO' and pagamento_contrato.status != 'PAGO':
                pagamento_contrato.status = 'PAGO'
                pagamento_contrato.data_pagamento = instance.data_pagamento or timezone.now().date()
                pagamento_contrato.save()
                logger.info(f"Pagamento {pagamento_contrato.id} atualizado para PAGO.")
                
            elif status_novo in ['CANCELADO', 'RESCINDIDO'] and pagamento_contrato.status not in ['PAGO', 'CANCELADO']:
                pagamento_contrato.status = 'CANCELADO'
                pagamento_contrato.save()
                
        except Exception as e:
            logger.error(f"Erro ao sincronizar Transacao {instance.id}: {e}")


# ==============================================================================
# 2. SINAL DE ONBOARDING (Criação Automática de Dados Padrão) - VERSÃO STANDARD
# ==============================================================================
@receiver(post_save, sender=Imobiliaria)
def criar_financeiro_padrao(sender, instance, created, **kwargs):
    """
    Cria Conta Caixa, Categorias e Formas de Pagamento automaticamente
    assim que uma nova Imobiliária é cadastrada.
    """
    if created:
        logger.info(f"--- Iniciando setup financeiro para: {instance.nome} ---")
        
        try:
            # A. Criar Conta Padrão (Caixa)
            if not Conta.objects.filter(imobiliaria=instance).exists():
                Conta.objects.create(
                    imobiliaria=instance,
                    nome="Conta Principal (Caixa)",
                    saldo_inicial=0
                )

            # B. Criar Formas de Pagamento Padrão
            formas_padrao = [
                'Boleto Bancário',
                'Pix',
                'Transferência (TED/DOC)',
                'Cartão de Crédito',
                'Dinheiro'
            ]
            for nome_forma in formas_padrao:
                FormaPagamento.objects.get_or_create(
                    imobiliaria=instance, 
                    nome=nome_forma
                )

            # C. Criar Categorias de Receita
            categorias_receita = [
                'Receita de Aluguel',
                'Taxa de Administração',
                'Taxa de Intermediação (Venda)',
                'Receitas Financeiras'
            ]
            for cat in categorias_receita:
                Categoria.objects.get_or_create(
                    imobiliaria=instance,
                    nome=cat,
                    defaults={'tipo': 'RECEITA'}
                )

            # D. Criar Categorias de Despesa
            categorias_despesa = [
                'Repasse de Aluguel',
                'Manutenção de Imóvel',
                'Despesas Administrativas',
                'Impostos e Taxas',
                'Marketing e Publicidade'
            ]
            for cat in categorias_despesa:
                Categoria.objects.get_or_create(
                    imobiliaria=instance,
                    nome=cat,
                    defaults={'tipo': 'DESPESA'}
                )
            
            logger.info(f"--- Sucesso: Dados padrão criados para {instance.nome} ---")
                
        except Exception as e:
            logger.error(f"ERRO ao criar financeiro padrão para {instance.nome}: {e}")
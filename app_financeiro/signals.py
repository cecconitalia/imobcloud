# C:\wamp64\www\imobcloud\app_financeiro\signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import logging
from datetime import timedelta
from decimal import Decimal # Importado Decimal

# Importação do modelo principal (Imobiliaria)
from core.models import Imobiliaria

# Importações dos modelos do App Financeiro e Contratos
from app_contratos.models import Pagamento, Contrato
from .models import Transacao, Conta, FormaPagamento, Categoria

logger = logging.getLogger(__name__)

# ==============================================================================
# 1. SINAL DE SINCRONIZAÇÃO (Transação -> Pagamento de Aluguel)
#    Mantém o status do Pagamento (Contrato) igual ao da Transação Financeira.
# ==============================================================================
@receiver(post_save, sender=Transacao)
def sincronizar_pagamento_contrato(sender, instance, created, **kwargs):
    """
    Mantém o status do Pagamento (Contrato) igual ao da Transação Financeira.
    """
    if instance.contrato and instance.contrato.tipo_contrato == Contrato.TipoContrato.ALUGUEL:
        try:
            # Tenta encontrar o registro de Pagamento correspondente (se existir)
            pagamento_contrato = Pagamento.objects.filter(
                contrato=instance.contrato,
                data_vencimento=instance.data_vencimento
            ).first()
            
            if not pagamento_contrato:
                return

            status_novo = instance.status
            
            # Sincroniza o status PAGO
            if status_novo == 'PAGO' and pagamento_contrato.status != 'PAGO':
                pagamento_contrato.status = 'PAGO'
                # Usa a data de pagamento da Transação, ou data atual se não definida
                pagamento_contrato.data_pagamento = instance.data_pagamento or timezone.now().date()
                pagamento_contrato.save()
                logger.info(f"Pagamento {pagamento_contrato.id} atualizado para PAGO.")
                
            # Sincroniza o status CANCELADO/ATRASADO/PENDENTE
            elif status_novo in ['CANCELADO', 'RESCINDIDO', 'ATRASADO', 'PENDENTE'] and pagamento_contrato.status != status_novo:
                 # Evita retroceder PAGO para outro status
                if pagamento_contrato.status == 'PAGO':
                     return 
                     
                pagamento_contrato.status = status_novo
                pagamento_contrato.save()
                
        except Exception as e:
            logger.error(f"Erro ao sincronizar Transacao {instance.id}: {e}")

# ==============================================================================
# 2. SINAL DE GERAÇÃO DE REPASSE (Transacao Paga -> Cria Despesa)
# ==============================================================================
@receiver(post_save, sender=Transacao)
def create_repasse_on_payment(sender, instance, created, **kwargs):
    """
    Gera a transação de DESPESA (repasse) para o proprietário assim que a RECEITA
    do aluguel (Transacao) for marcada como PAGA.
    """
    # Se recém-criada (criada como PENDENTE) ou se não for paga, ignora
    if created or instance.status != 'PAGO':
        return

    contrato = instance.contrato

    # Condições para gerar o repasse:
    # 1. Deve ser uma RECEITA
    # 2. Deve estar ligada a um Contrato de Aluguel
    # 3. Não pode ser um repasse (transacao_origem deve ser None)
    if not (instance.tipo == 'RECEITA' and 
            contrato and 
            contrato.tipo_contrato == Contrato.TipoContrato.ALUGUEL and 
            not instance.transacao_origem):
        return

    # 1. Checa se o repasse para esta transação específica JÁ foi gerado
    if Transacao.objects.filter(transacao_origem=instance, tipo='DESPESA').exists():
        return

    # 2. CALCULA OS VALORES
    valor_aluguel_bruto = instance.valor
    taxa_adm_percentual = contrato.taxa_administracao_percentual
    
    # Valor da Taxa (Fica com a imobiliária)
    taxa_adm_valor = (valor_aluguel_bruto * taxa_adm_percentual / Decimal(100)).quantize(Decimal('0.01'))
    
    # Valor Líquido (Vai para o proprietário)
    valor_repasse_liquido = valor_aluguel_bruto - taxa_adm_valor

    # 3. GARANTE QUE A CATEGORIA DE REPASSE EXISTA
    try:
        categoria_repasse = Categoria.objects.get(
            imobiliaria=contrato.imobiliaria,
            nome='Repasse de Aluguel',
            tipo='DESPESA'
        )
    except Categoria.DoesNotExist:
        # Cria a categoria se não existir (garantindo que não haverá erro de FK)
        categoria_repasse = Categoria.objects.create(
            imobiliaria=contrato.imobiliaria,
            nome='Repasse de Aluguel',
            tipo='DESPESA'
        )

    # 4. CRIA A TRANSAÇÃO DE DESPESA (REPASSE)
    # Assume que o dinheiro foi para a mesma conta da Receita.
    Transacao.objects.create(
        imobiliaria=contrato.imobiliaria,
        descricao=f"Repasse Aluguel: {contrato.imovel.titulo_anuncio or contrato.imovel.logradouro} (Ref: {instance.data_vencimento.strftime('%m/%Y')})",
        valor=valor_repasse_liquido,
        data_transacao=timezone.now().date(),
        data_vencimento=timezone.now().date() + timedelta(days=5), # Vencimento 5 dias após o recebimento
        tipo='DESPESA',
        status='PENDENTE', # Repasse PENDENTE de pagamento
        categoria=categoria_repasse,
        conta=instance.conta,
        cliente=contrato.proprietario,
        imovel=contrato.imovel,
        contrato=contrato,
        transacao_origem=instance, # Linka à RECEITA original
        observacoes=f"Valor Bruto: R$ {valor_aluguel_bruto}. Taxa Adm ({taxa_adm_percentual}%): R$ {taxa_adm_valor}. Líquido a repassar: R$ {valor_repasse_liquido}."
    )
    logger.info(f"SUCESSO REPASSE: Criada Despesa de Repasse para Transacao {instance.id}.")


# ==============================================================================
# 3. SINAL DE ONBOARDING (Criação Automática de Dados Padrão) - VERSÃO STANDARD
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
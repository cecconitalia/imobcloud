from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

# Importação do modelo principal (Tenant)
from core.models import Imobiliaria

# Importações dos modelos do App Financeiro e Contratos
from app_contratos.models import Pagamento, Contrato
from .models import Transacao, Conta, FormaPagamento, Categoria

logger = logging.getLogger(__name__)

# ==============================================================================
# 1. SINAL DE ONBOARDING (Criação Automática de Dados Padrão ao criar Imobiliária)
# ==============================================================================
@receiver(post_save, sender=Imobiliaria)
def criar_dados_iniciais_financeiro(sender, instance, created, **kwargs):
    """
    Cria automaticamente a estrutura financeira básica para um novo Tenant.
    Garante que a imobiliária já comece operacional.
    """
    if created:
        logger.info(f"--- Iniciando Setup Financeiro: {instance.nome} ---")
        
        try:
            # A. Criar Conta Padrão (Caixa Interno)
            # Usamos get_or_create para garantir idempotência
            conta_padrao, _ = Conta.objects.get_or_create(
                imobiliaria=instance,
                nome="Caixa Interno",
                defaults={
                    'saldo_inicial': Decimal('0.00'),
                    'ativo': True
                }
            )

            # B. Criar Formas de Pagamento Padrão
            formas = [
                'Dinheiro',
                'Pix',
                'Boleto Bancário',
                'Cartão de Crédito',
                'Transferência Bancária',
            ]
            for nome_forma in formas:
                FormaPagamento.objects.get_or_create(
                    imobiliaria=instance,
                    nome=nome_forma,
                    defaults={'ativo': True}
                )

            # C. Criar Categorias de Receita
            categorias_receita = [
                'Aluguel',
                'Taxa de Administração',
                'Comissão de Venda',
                'Multas e Juros',
                'Receitas Financeiras',
            ]
            for nome_cat in categorias_receita:
                Categoria.objects.get_or_create(
                    imobiliaria=instance,
                    nome=nome_cat,
                    tipo='RECEITA',
                    defaults={'ativa': True}
                )

            # D. Criar Categorias de Despesa
            categorias_despesa = [
                'Repasse de Proprietário',
                'Manutenção de Imóvel',
                'Publicidade e Marketing',
                'Salários e Encargos',
                'Impostos e Taxas',
                'Custos Operacionais',
            ]
            for nome_cat in categorias_despesa:
                Categoria.objects.get_or_create(
                    imobiliaria=instance,
                    nome=nome_cat,
                    tipo='DESPESA',
                    defaults={'ativa': True}
                )

            logger.info(f"--- Setup Financeiro Concluído para {instance.nome} ---")

        except Exception as e:
            logger.error(f"Erro no Onboarding Financeiro da Imobiliária {instance.id}: {e}")


# ==============================================================================
# 2. SINAL DE SINCRONIZAÇÃO (Transação -> Pagamento de Aluguel)
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
            
            # Sincroniza o status PAGO
            if status_novo == 'PAGO' and pagamento_contrato.status != 'PAGO':
                pagamento_contrato.status = 'PAGO'
                pagamento_contrato.data_pagamento = instance.data_pagamento or timezone.now().date()
                pagamento_contrato.save()
                logger.info(f"Pagamento {pagamento_contrato.id} atualizado para PAGO via Transação {instance.id}.")
                
            # Sincroniza outros status (exceto se já estiver PAGO no contrato)
            elif status_novo in ['CANCELADO', 'RESCINDIDO', 'ATRASADO', 'PENDENTE']:
                if pagamento_contrato.status != 'PAGO' and pagamento_contrato.status != status_novo:
                    pagamento_contrato.status = status_novo
                    pagamento_contrato.save()
                
        except Exception as e:
            logger.error(f"Erro ao sincronizar Transacao {instance.id} com Contrato: {e}")


# ==============================================================================
# 3. SINAL DE GERAÇÃO DE REPASSE (Transação Paga -> Cria Despesa para Proprietário)
# ==============================================================================
@receiver(post_save, sender=Transacao)
def create_repasse_on_payment(sender, instance, created, **kwargs):
    """
    Gera a transação de DESPESA (repasse) para o proprietário assim que a RECEITA
    do aluguel for marcada como PAGA.
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

    # 1. Checa se o repasse para esta transação específica JÁ foi gerado (evita duplicidade)
    if Transacao.objects.filter(transacao_origem=instance, tipo='DESPESA').exists():
        return

    try:
        # 2. CALCULA OS VALORES
        valor_aluguel_bruto = instance.valor
        taxa_adm_percentual = contrato.taxa_administracao_percentual or Decimal('0.00')
        
        # Valor da Taxa (Fica com a imobiliária)
        taxa_adm_valor = (valor_aluguel_bruto * taxa_adm_percentual / Decimal('100')).quantize(Decimal('0.01'))
        
        # Valor Líquido (Vai para o proprietário)
        valor_repasse_liquido = valor_aluguel_bruto - taxa_adm_valor

        # 3. GARANTE QUE A CATEGORIA DE REPASSE EXISTA PARA ESTE TENANT
        categoria_repasse, _ = Categoria.objects.get_or_create(
            imobiliaria=instance.imobiliaria,
            nome='Repasse de Proprietário',
            tipo='DESPESA',
            defaults={'ativa': True}
        )

        # 4. CRIA A TRANSAÇÃO DE DESPESA (REPASSE)
        Transacao.objects.create(
            imobiliaria=instance.imobiliaria,
            descricao=f"Repasse Aluguel: {contrato.imovel.titulo_anuncio or contrato.imovel.logradouro} (Ref: {instance.data_vencimento.strftime('%m/%Y')})",
            valor=valor_repasse_liquido,
            data_transacao=timezone.now().date(),
            data_vencimento=timezone.now().date() + timedelta(days=5), # Regra: 5 dias após o recebimento
            tipo='DESPESA',
            status='PENDENTE',
            categoria=categoria_repasse,
            conta=instance.conta,
            cliente=contrato.cliente, # O beneficiário da despesa é o proprietário (vinculado ao contrato)
            imovel=contrato.imovel,
            contrato=contrato,
            transacao_origem=instance, # Linka à RECEITA original
            observacoes=(
                f"Lançamento Automático.\n"
                f"Valor Bruto: R$ {valor_aluguel_bruto}\n"
                f"Taxa Adm ({taxa_adm_percentual}%): R$ {taxa_adm_valor}\n"
                f"Líquido a repassar: R$ {valor_repasse_liquido}"
            )
        )
        logger.info(f"REPASSE GERADO: Criada Despesa para Proprietário ref. Transacao {instance.id}.")

    except Exception as e:
        logger.error(f"Erro ao gerar repasse para Transacao {instance.id}: {e}")
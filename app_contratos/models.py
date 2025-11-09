# Em app_contratos/models.py

from django.db import models
from core.models import Imobiliaria
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from django.utils import timezone
from app_financeiro.models import FormaPagamento

class Contrato(models.Model):
    
    class TipoContrato(models.TextChoices):
        VENDA = 'VENDA', 'Venda'
        ALUGUEL = 'ALUGUEL', 'Aluguel'

    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        ATIVO = 'ATIVO', 'Ativo'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'
        RESCINDIDO = 'RESCINDIDO', 'Rescindido'
        INATIVO = 'INATIVO', 'Inativo'
    
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    
    tipo_contrato = models.CharField(
        max_length=50, 
        verbose_name="Tipo de Contrato", 
        choices=TipoContrato.choices
    )
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, verbose_name="Imóvel")
    inquilino = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name="contratos_aluguel", 
        verbose_name="Inquilino"
    )
    proprietario = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="contratos_propriedade",
        verbose_name="Proprietário"
    )

    # ==================================================================
    # CORREÇÃO CRÍTICA: O seu ficheiro tinha 'fiador = models.ForeignKey'.
    # O correto é 'fiadores = models.ManyToManyField' para aceitar
    # a lista [1, 2] enviada pelo seu ContratoFormView.vue.
    # ==================================================================
    fiadores = models.ManyToManyField(
        Cliente,
        related_name="contratos_como_fiador",
        verbose_name="Fiadores",
        blank=True 
    )
    
    aluguel = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name="Valor do Aluguel (Mensal)",
        null=True, 
        blank=True,
        help_text="Usado para gerar parcelas de aluguel."
    )
    
    valor_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name="Valor Total do Contrato (Venda)",
        null=True, # Permitir nulo para aluguel
        blank=True
    )
    informacoes_adicionais = models.TextField(
        blank=True, null=True, verbose_name="Informações Adicionais"
    )
    duracao_meses = models.PositiveIntegerField(
        default=12,
        verbose_name="Duração do Contrato (em meses)",
        help_text="Usado para gerar as parcelas de aluguel.",
        null=True, # Permitir nulo para venda
        blank=True
    )
    status_contrato = models.CharField(
        max_length=50, 
        default=Status.PENDENTE, 
        verbose_name="Status do Contrato", 
        choices=Status.choices
    )
    
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Término (se aplicável)")
    data_assinatura = models.DateField(verbose_name="Data de Assinatura")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")

    formas_pagamento = models.ManyToManyField(
        'app_financeiro.FormaPagamento',
        blank=True,
        verbose_name="Formas de Pagamento Aceitas"
    )
    
    conteudo_personalizado = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Conteúdo Personalizado do Contrato",
        help_text="Armazena o conteúdo HTML do contrato após a edição."
    )

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ['-data_cadastro']

    def __str__(self):
        return f"Contrato de {self.get_tipo_contrato_display()} - {self.imovel.logradouro} ({self.imobiliaria.nome})"


class Pagamento(models.Model):
    STATUS_PAGAMENTO_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('ATRASADO', 'Atrasado'),
        ('CANCELADO', 'Cancelado'),
    ]

    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name="pagamentos", verbose_name="Contrato")
    valor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor do Pagamento")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_pagamento = models.DateField(null=True, blank=True, verbose_name="Data de Pagamento")
    status = models.CharField(max_length=20, choices=STATUS_PAGAMENTO_CHOICES, default='PENDENTE', verbose_name="Status")
    
    forma_pagamento_recebida = models.ForeignKey(
        'app_financeiro.FormaPagamento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Forma de Pagamento Recebida"
    )

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['data_vencimento']

    def __str__(self):
        return f"Pagamento de {self.valor} para o contrato #{self.contrato.id} com vencimento em {self.data_vencimento}"

    @property
    def esta_atrasado(self):
        return timezone.now().date() > self.data_vencimento and self.status == 'PENDENTE'
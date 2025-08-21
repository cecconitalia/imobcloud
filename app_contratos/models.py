# Em app_contratos/models.py

from django.db import models
from core.models import Imobiliaria
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from django.utils import timezone

class Contrato(models.Model):
    # --- NOVO: Campo de CHOICES para o tipo de contrato ---
    TIPO_CONTRATO_CHOICES = [
        ('Venda', 'Venda'),
        ('Aluguel', 'Aluguel')
    ]
    
    # --- NOVO: Campo de CHOICES para o status ---
    STATUS_CONTRATO_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Ativo', 'Ativo'),
        ('Concluído', 'Concluído'),
        ('Rescindido', 'Rescindido'),
        ('Inativo', 'Inativo')
    ]
    
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    
    # --- Campos para associar o contrato aos envolvidos ---
    tipo_contrato = models.CharField(
        max_length=50, 
        verbose_name="Tipo de Contrato", 
        choices=TIPO_CONTRATO_CHOICES
    )
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, verbose_name="Imóvel")
    # NOVO: Chave estrangeira para o inquilino. Assume-se que o cliente_id é o inquilino.
    inquilino = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name="contratos_aluguel", 
        verbose_name="Inquilino"
    )
    # NOVO: Chave estrangeira para o proprietário. Busca-se pelo proprietário no modelo Imovel.
    # O on_delete=models.PROTECT evita a exclusão de um proprietário com contrato ativo.
    proprietario = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="contratos_propriedade",
        verbose_name="Proprietário"
    )

    # --- Campos do contrato ---
    valor_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name="Valor Total do Contrato"
    )
    condicoes_pagamento = models.TextField(verbose_name="Condições de Pagamento")
    duracao_meses = models.PositiveIntegerField(
        default=12,
        verbose_name="Duração do Contrato (em meses)",
        help_text="Usado para gerar as parcelas de aluguel."
    )
    status_contrato = models.CharField(
        max_length=50, 
        default='Pendente', # NOVO: O status padrão é Pendente
        verbose_name="Status do Contrato", 
        choices=STATUS_CONTRATO_CHOICES
    )
    
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Término (se aplicável)")
    data_assinatura = models.DateField(verbose_name="Data de Assinatura")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ['-data_cadastro']

    def __str__(self):
        return f"Contrato de {self.tipo_contrato} - {self.imovel.endereco} ({self.imobiliaria.nome})"


class Pagamento(models.Model):
    """
    Representa uma parcela de pagamento de um contrato,
    especialmente útil para aluguéis.
    """
    STATUS_PAGAMENTO_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('ATRASADO', 'Atrasado'),
        # NOVO: Adicionado status CANCELADO
        ('CANCELADO', 'Cancelado'),
    ]

    # NOVO: Campo para registrar a forma de pagamento
    FORMA_PAGAMENTO_CHOICES = [
        ('BOLETO', 'Boleto'),
        ('PIX', 'PIX'),
        ('TRANSFERENCIA', 'Transferência Bancária'),
        ('DINHEIRO', 'Dinheiro'),
        ('CARTAO', 'Cartão de Crédito/Débito'),
        ('OUTRO', 'Outro'),
    ]

    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name="pagamentos", verbose_name="Contrato")
    valor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor do Pagamento")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_pagamento = models.DateField(null=True, blank=True, verbose_name="Data de Pagamento")
    status = models.CharField(max_length=20, choices=STATUS_PAGAMENTO_CHOICES, default='PENDENTE', verbose_name="Status")
    forma_pagamento_recebida = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        null=True, blank=True,
        verbose_name="Forma de Pagamento"
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
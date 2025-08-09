# app_financeiro/models.py

from django.db import models
from core.models import Imobiliaria
from django.utils import timezone
from django.core.validators import MinValueValidator
from app_imoveis.models import Imovel
# --- ADICIONADO: Importar o modelo Contrato ---
from app_contratos.models import Contrato

class Categoria(models.Model):
    # (Seu modelo Categoria continua igual)
    TIPO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    ]
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE)
    pai = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategorias')
    
    class Meta:
        verbose_name = "Categoria Financeira"
        verbose_name_plural = "Categorias Financeiras"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.imobiliaria.nome})"

class ContaBancaria(models.Model):
    # (Seu modelo ContaBancaria continua igual)
    nome = models.CharField(max_length=100)
    banco = models.CharField(max_length=100)
    agencia = models.CharField(max_length=50)
    numero_conta = models.CharField(max_length=50)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    saldo_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Conta Bancária"
        verbose_name_plural = "Contas Bancárias"
        ordering = ['banco', 'nome']
        unique_together = ('imobiliaria', 'numero_conta')

    def __str__(self):
        return f"{self.nome} - {self.banco} ({self.imobiliaria.nome})"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.saldo_atual = self.saldo_inicial
        super().save(*args, **kwargs)

# --- MODELO TRANSAÇÃO TOTALMENTE ATUALIZADO ---
class Transacao(models.Model):
    TIPO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    ]
    # --- NOVO: Status da transação ---
    STATUS_CHOICES = (
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('ATRASADO', 'Atrasado'),
        ('CANCELADO', 'Cancelado'),
    )

    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    
    # --- ALTERADO: 'data' foi renomeado para 'data_vencimento' ---
    data_vencimento = models.DateField(default=timezone.now, verbose_name="Data de Vencimento")
    
    # --- NOVOS CAMPOS ---
    data_pagamento = models.DateField(verbose_name="Data de Pagamento", null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')

    # --- RELACIONAMENTOS ---
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.PROTECT)
    imovel = models.ForeignKey(Imovel, on_delete=models.SET_NULL, null=True, blank=True)
    # --- NOVO: Link com o Contrato ---
    contrato = models.ForeignKey(Contrato, on_delete=models.SET_NULL, null=True, blank=True, related_name="transacoes")
    
    class Meta:
        verbose_name = "Transação/Conta"
        verbose_name_plural = "Transações e Contas"
        ordering = ['-data_vencimento']

    def __str__(self):
        return f"({self.tipo}) {self.descricao} - {self.valor} - Venc: {self.data_vencimento.strftime('%d/%m/%Y')}"

    def save(self, *args, **kwargs):
        # Lógica para definir o status automaticamente
        if self.data_pagamento and self.status in ['PENDENTE', 'ATRASADO']:
            self.status = 'PAGO'
        elif not self.data_pagamento and self.status == 'PAGO':
             self.status = 'PENDENTE' # Volta a pendente se a data de pagamento for removida

        super().save(*args, **kwargs)
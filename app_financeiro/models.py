from django.db import models
from django.utils import timezone # Adicione esta linha
from core.models import Imobiliaria
from app_clientes.models import Oportunidade
from app_contratos.models import Contrato

class Categoria(models.Model):
    TIPO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    ]
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo")

    class Meta:
        verbose_name = "Categoria Financeira"
        verbose_name_plural = "Categorias Financeiras"
        unique_together = ('imobiliaria', 'nome')

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class ContaBancaria(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    nome = models.CharField(max_length=100, verbose_name="Nome da Conta")
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Saldo Inicial")
    saldo_atual = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Saldo Atual")
    banco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banco")
    agencia = models.CharField(max_length=20, blank=True, null=True, verbose_name="Agência")
    numero_conta = models.CharField(max_length=50, blank=True, null=True, verbose_name="Número da Conta")

    class Meta:
        verbose_name = "Conta Bancária"
        verbose_name_plural = "Contas Bancárias"

    def __str__(self):
        return f"{self.nome} ({self.imobiliaria.nome})"

class Transacao(models.Model):
    TIPO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    ]
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo de Transação")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor")
    data = models.DateField(default=timezone.now, verbose_name="Data da Transação")
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoria")
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Conta Bancária")
    
    oportunidade = models.ForeignKey(Oportunidade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Oportunidade (opcional)")
    contrato = models.ForeignKey(Contrato, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Contrato (opcional)")

    class Meta:
        verbose_name = "Transação Financeira"
        verbose_name_plural = "Transações Financeiras"
        ordering = ['-data']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao}"
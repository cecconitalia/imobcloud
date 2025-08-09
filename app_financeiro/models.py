from django.db import models
from core.models import Imobiliaria
from django.utils import timezone
from django.core.validators import MinValueValidator
from app_imoveis.models import Imovel  # Importa o modelo Imovel

class Categoria(models.Model):
    # A categoria principal
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

class Transacao(models.Model):
    TIPO_CHOICES = [
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    ]

    data = models.DateField(default=timezone.now)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=255)
    tipo = models.CharField(max_length=7, choices=TIPO_CHOICES)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.PROTECT)
    imovel = models.ForeignKey(Imovel, on_delete=models.SET_NULL, null=True, blank=True) # NOVO CAMPO
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Transação Financeira"
        verbose_name_plural = "Transações Financeiras"
        ordering = ['-data']

    def __str__(self):
        return f"({self.tipo}) {self.descricao} - {self.valor} em {self.data}"
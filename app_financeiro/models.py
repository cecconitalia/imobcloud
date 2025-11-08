# C:\wamp64\www\ImobCloud\app_financeiro\models.py

from django.db import models
from core.models import Imobiliaria
from app_clientes.models import Cliente
from app_imoveis.models import Imovel

class Categoria(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=[('RECEITA', 'Receita'), ('DESPESA', 'Despesa')])

    class Meta:
        unique_together = ('imobiliaria', 'nome')
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return f"{self.nome} ({self.tipo})"

class Conta(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('imobiliaria', 'nome')
        verbose_name = "Conta"
        verbose_name_plural = "Contas"

    def __str__(self):
        return self.nome

class FormaPagamento(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)

    class Meta:
        unique_together = ('imobiliaria', 'nome')
        verbose_name = "Forma de Pagamento"
        verbose_name_plural = "Formas de Pagamento"

    def __str__(self):
        return self.nome

class Transacao(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_transacao = models.DateField()
    data_vencimento = models.DateField()
    tipo = models.CharField(max_length=10, choices=[('RECEITA', 'Receita'), ('DESPESA', 'Despesa')])
    status = models.CharField(max_length=20, choices=[('PENDENTE', 'Pendente'), ('PAGO', 'Pago'), ('ATRASADO', 'Atrasado')], default='PENDENTE')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    conta = models.ForeignKey(Conta, on_delete=models.SET_NULL, null=True, blank=True)
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.SET_NULL, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    imovel = models.ForeignKey(Imovel, on_delete=models.SET_NULL, null=True, blank=True)
    
    contrato = models.ForeignKey(
        'app_contratos.Contrato', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='transacoes'
    )
    
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        ordering = ['-data_vencimento']

    def __str__(self):
        return self.descricao

    @property
    def cliente_nome(self):
        """
        Retorna o nome do cliente associado a esta transação,
        seja através do campo cliente ou do contrato.
        """
        # CORREÇÃO: A lógica que usava 'nome_completo' estava errada.
        # Esta lógica verifica se o cliente é PF ou PJ.
        cliente_obj = None
        if self.cliente:
            cliente_obj = self.cliente
        elif self.contrato and self.contrato.inquilino:
            cliente_obj = self.contrato.inquilino

        if cliente_obj:
            try:
                # Verifica se é PJ e tem razao_social
                if cliente_obj.tipo_pessoa == 'JURIDICA' and cliente_obj.razao_social:
                    return cliente_obj.razao_social
            except AttributeError:
                # Caso o modelo Cliente não tenha 'tipo_pessoa' ou 'razao_social', 
                # apenas retorna o 'nome'
                pass
            
            # Retorna 'nome' para PF ou como fallback
            return cliente_obj.nome 
            
        return "Cliente não informado"
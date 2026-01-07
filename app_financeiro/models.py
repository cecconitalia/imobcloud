# C:\wamp64\www\ImobCloud\app_financeiro\models.py

from django.db import models
from core.models import Imobiliaria
from app_clientes.models import Cliente
from app_imoveis.models import Imovel
from django.utils import timezone

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
    data_transacao = models.DateField(
        default=timezone.now, 
        verbose_name="Data do Lançamento"
    )
    data_vencimento = models.DateField()
    data_pagamento = models.DateField(
        null=True, 
        blank=True, 
        help_text="Data efetiva do pagamento (apenas se status for 'PAGO')."
    )
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
    
    # [NOVO CAMPO] Para ligar o repasse (DESPESA) à transação original (RECEITA)
    transacao_origem = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transacoes_repasse',
        verbose_name="Transação de Origem",
        help_text="Transação de Receita que originou este Repasse/Despesa."
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
        (Lógica refatorada para maior robustez)
        """
        cliente_obj = self.cliente
        # Prioriza o cliente associado diretamente à transação
        if not cliente_obj and self.contrato and hasattr(self.contrato, 'inquilino'):
            # Se não houver, tenta buscar o inquilino do contrato (comum em Contas a Receber de aluguéis)
            cliente_obj = self.contrato.inquilino

        if cliente_obj:
            # Uso de getattr para evitar erros de AttributeError caso o modelo Cliente mude
            tipo_pessoa = getattr(cliente_obj, 'tipo_pessoa', 'FISICA')
            razao_social = getattr(cliente_obj, 'razao_social', None)
            nome = getattr(cliente_obj, 'nome', None)
            
            # Tenta retornar a Razão Social para PJ, caso contrário retorna o Nome
            if tipo_pessoa == 'JURIDICA' and razao_social:
                return razao_social
            
            return nome if nome else "Nome Indisponível"
            
        return "Cliente não informado"
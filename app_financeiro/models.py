from django.db import models
from core.models import Imobiliaria
from app_clientes.models import Cliente
from app_imoveis.models import Imovel
from django.utils import timezone

class Categoria(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, related_name='categorias_financeiras')
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=[('RECEITA', 'Receita'), ('DESPESA', 'Despesa')])
    ativa = models.BooleanField(default=True)

    class Meta:
        unique_together = ('imobiliaria', 'nome', 'tipo')
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"

class Conta(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, related_name='contas_financeiras')
    nome = models.CharField(max_length=100)
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ativo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('imobiliaria', 'nome')
        verbose_name = "Conta"
        verbose_name_plural = "Contas"

    def __str__(self):
        return self.nome

class FormaPagamento(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, related_name='formas_pagamento_financeiro')
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('imobiliaria', 'nome')
        verbose_name = "Forma de Pagamento"
        verbose_name_plural = "Formas de Pagamento"

    def __str__(self):
        return self.nome

class Transacao(models.Model):
    TIPO_CHOICES = [('RECEITA', 'Receita'), ('DESPESA', 'Despesa')]
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('ATRASADO', 'Atrasado'),
        ('CANCELADO', 'Cancelado')
    ]

    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, related_name='transacoes')
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    
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
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, null=True, blank=True)
    conta = models.ForeignKey(Conta, on_delete=models.PROTECT, null=True, blank=True)
    forma_pagamento = models.ForeignKey(FormaPagamento, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Relacionamentos de Contexto
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacoes_cliente')
    imovel = models.ForeignKey(Imovel, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacoes_imovel')
    
    contrato = models.ForeignKey(
        'app_contratos.Contrato', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='transacoes'
    )
    
    # Campo para vincular o repasse (DESPESA) à transação original de recebimento (RECEITA)
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
        return f"{self.descricao} - {self.valor} ({self.status})"

    @property
    def cliente_nome(self):
        """
        Retorna o nome amigável do cliente associado.
        Lógica:
        1. Verifica o campo 'cliente' direto da transação.
        2. Se for uma receita de aluguel sem cliente setado, busca o inquilino no contrato.
        3. Se for um repasse (despesa), busca o proprietário no contrato.
        """
        cliente_obj = self.cliente
        
        # Fallback para Contrato se o cliente não estiver preenchido diretamente
        if not cliente_obj and self.contrato:
            if self.tipo == 'RECEITA':
                cliente_obj = getattr(self.contrato, 'cliente', None) # Geralmente o inquilino no contrato
            else:
                # Se for despesa (provável repasse), tenta pegar o proprietário do imóvel vinculado
                if self.contrato.imovel:
                    cliente_obj = self.contrato.imovel.proprietario

        if cliente_obj:
            tipo_pessoa = getattr(cliente_obj, 'tipo_pessoa', 'FISICA')
            razao_social = getattr(cliente_obj, 'razao_social', None)
            nome = getattr(cliente_obj, 'nome', None)
            
            if tipo_pessoa == 'JURIDICA' and razao_social:
                return razao_social
            return nome or "Nome Indisponível"
            
        return "Não informado"
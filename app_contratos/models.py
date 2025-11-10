# Em app_contratos/models.py

from django.db import models
from core.models import Imobiliaria
from app_imoveis.models import Imovel
from app_clientes.models import Cliente
from django.utils import timezone
from app_financeiro.models import FormaPagamento
from decimal import Decimal 
from django.core.validators import MinValueValidator, MaxValueValidator
# Imports ADICIONADOS (movidos de views.py)
from app_financeiro.models import Transacao, Categoria, Conta
from dateutil.relativedelta import relativedelta


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
    
    taxa_administracao_percentual = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('10.00'), 
        verbose_name="Taxa de Administração (%)",
        help_text="Percentual retido pela imobiliária sobre o aluguel."
    )
    
    comissao_venda_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('6.00'), 
        verbose_name="Comissão de Venda (%)",
        help_text="Percentual de comissão sobre o valor total da venda."
    )
    
    valor_comissao_acordado = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor Final da Comissão (R$)",
        help_text="Valor final acordado. Usado para lançar a RECEITA."
    )
    
    valor_total = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        verbose_name="Valor Total do Contrato (Venda)",
        null=True, 
        blank=True
    )
    informacoes_adicionais = models.TextField(
        blank=True, null=True, verbose_name="Informações Adicionais"
    )
    duracao_meses = models.PositiveIntegerField(
        default=12,
        verbose_name="Duração do Contrato (em meses)",
        help_text="Usado para gerar as parcelas de aluguel.",
        null=True, 
        blank=True
    )
        
    data_primeiro_vencimento = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Data do 1º Vencimento (Aluguel)",
        help_text="Data do primeiro vencimento para gerar as parcelas de aluguel."
    )
    
    data_vencimento_venda = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Data Venc. Comissão/Quitação (Venda)",
        help_text="Data limite para o pagamento da comissão ou quitação da venda."
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

    # --- MÉTODOS MOVIDOS DE views.py PARA models.py ---

    def gerar_financeiro_aluguel(self):
        """ Helper para gerar parcelas de aluguel """
        imobiliaria = self.imobiliaria
        
        if not self.aluguel or not self.duracao_meses or not self.data_primeiro_vencimento:
             print(f"ERRO ALUGUEL: Contrato {self.id} sem Valor/Duração/Data do 1º Vencimento. Geração ignorada.")
             return False
             
        Pagamento.objects.filter(contrato=self, status='PENDENTE').delete()
        Transacao.objects.filter(contrato=self, status='PENDENTE', tipo='RECEITA').delete()
        
        data_base_vencimento = self.data_primeiro_vencimento
        duracao = self.duracao_meses
        
        try:
             categoria_aluguel = Categoria.objects.get(imobiliaria=imobiliaria, nome='Receita de Aluguel')
        except Categoria.DoesNotExist:
             categoria_aluguel = Categoria.objects.create(imobiliaria=imobiliaria, nome='Receita de Aluguel', tipo='RECEITA')
             
        conta_padrao = Conta.objects.filter(imobiliaria=imobiliaria).first()
        
        for i in range(duracao):
             data_parcela = data_base_vencimento + relativedelta(months=i)
             
             Pagamento.objects.create(
                 contrato=self,
                 data_vencimento=data_parcela,
                 valor=self.aluguel, 
                 status='PENDENTE'
             )
             
             Transacao.objects.create(
                 imobiliaria=imobiliaria,
                 descricao=f'Aluguel {i+1}/{duracao} - Imóvel: {self.imovel.logradouro}',
                 valor=self.aluguel,
                 data_transacao=timezone.now().date(), 
                 data_vencimento=data_parcela,
                 tipo='RECEITA',
                 status='PENDENTE',
                 categoria=categoria_aluguel,
                 conta=conta_padrao,
                 cliente=self.inquilino,
                 imovel=self.imovel,
                 contrato=self
             )
        print(f"SUCESSO ALUGUEL: {duracao} parcelas geradas para Contrato {self.id}.")
        return True

    def criar_transacao_comissao(self):
        """
        Cria a transação de RECEITA (pendente) para a comissão de venda.
        """
        
        descricao_base = f"Comissão Venda #{self.id}: {self.imovel.logradouro}"
        if Transacao.objects.filter(contrato=self, tipo='RECEITA', descricao__startswith=f"Comissão Venda #{self.id}").exists():
            print(f"AVISO VENDA: Lançamento de comissão para Contrato {self.id} já existe. Ignorando.")
            return False

        valor_comissao = self.valor_comissao_acordado 
        if not valor_comissao or valor_comissao <= 0:
            print(f"AVISO VENDA: Contrato {self.id} sem Valor de Comissão Acordado (R$ {valor_comissao}). Lançamento ignorado.")
            return False

        try:
            categoria_comissao, created = Categoria.objects.get_or_create(
                imobiliaria=self.imobiliaria,
                nome='Comissão de Venda', 
                tipo='RECEITA'
            )
            if created:
                print(f"AVISO VENDA: Categoria 'Comissão de Venda' (RECEITA) criada automaticamente.")
        except Exception as e:
            print(f"ERRO CRÍTICO VENDA: Falha ao obter/criar Categoria de Comissão. Erro: {e}.")
            return False

        data_base = timezone.now().date()
        data_vencimento = self.data_vencimento_venda 

        Transacao.objects.create(
            imobiliaria=self.imobiliaria,
            descricao=descricao_base,
            valor=valor_comissao,
            tipo='RECEITA',
            status='PENDENTE',
            data_transacao=data_base,
            data_vencimento=data_vencimento,
            
            categoria=categoria_comissao,
            cliente=self.proprietario, # A comissão é devida pelo Proprietário
            imovel=self.imovel,
            contrato=self,
            
            observacoes=f"Comissão de Venda gerada automaticamente. Valor de venda: R$ {self.valor_total}. Comissão baseada no valor acordado: R$ {valor_comissao.quantize(Decimal('0.01'))}."
        )
        print(f"SUCESSO VENDA: Criada Receita de Comissão R$ {valor_comissao} para o contrato {self.id}.")
        return True

    # --- FIM DOS MÉTODOS MOVIDOS ---


    def save(self, *args, **kwargs):
        # --- LÓGICA DE FAILSAFE (Cinto de Segurança) ---
        # Garante que o proprietário do contrato seja sincronizado
        # com o proprietário do imóvel selecionado, caso a view não o faça.
        if self.imovel and self.imovel.proprietario:
            self.proprietario = self.imovel.proprietario
        # --- FIM DA LÓGICA DE FAILSAFE ---
        
        # Lógica de cálculo inicial da comissão
        if self.tipo_contrato == self.TipoContrato.VENDA and self.valor_total and self.valor_comissao_acordado is None:
            percentual = Decimal(self.comissao_venda_percentual) / Decimal(100) 
            self.valor_comissao_acordado = self.valor_total * percentual
        
        super().save(*args, **kwargs)

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
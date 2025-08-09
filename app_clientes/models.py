# C:\wamp64\www\ImobCloud\app_clientes\models.py
from django.db import models
from core.models import Imobiliaria
from django.conf import settings
from django.utils import timezone

class Cliente(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf_cnpj = models.CharField(max_length=18, unique=False, verbose_name="CPF/CNPJ")
    email = models.EmailField(verbose_name="E-mail")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    preferencias_imovel = models.TextField(blank=True, null=True, verbose_name="Preferências de Imóvel")
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        unique_together = ('imobiliaria', 'cpf_cnpj')

    def __str__(self):
        return f"{self.nome_completo} ({self.imobiliaria.nome})"


class Visita(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    imovel = models.ForeignKey('app_imoveis.Imovel', on_delete=models.CASCADE, verbose_name="Imóvel") 
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    data_hora = models.DateTimeField(verbose_name="Data e Hora da Visita")
    status = models.CharField(max_length=50, default='Agendada', verbose_name="Status da Visita", choices=[('Agendada', 'Agendada'), ('Realizada', 'Realizada'), ('Cancelada', 'Cancelada')])
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")

    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        ordering = ['data_hora']

    def __str__(self):
        return f"Visita de {self.cliente.nome_completo} a {self.imovel.endereco} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"


class Atividade(models.Model):
    TIPO_ATIVIDADE_CHOICES = [
        ('NOTA', 'Nota'),
        ('TAREFA', 'Tarefa'),
        ('VISITA', 'Visita Agendada'),
        ('CONTRATO', 'Contrato Criado'),
        ('EMAIL', 'Email'),
        ('LIGACAO', 'Ligação'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="atividades", verbose_name="Cliente")
    tipo = models.CharField(max_length=20, choices=TIPO_ATIVIDADE_CHOICES, verbose_name="Tipo de Atividade")
    descricao = models.TextField(verbose_name="Descrição da Atividade")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Registrado por"
    )
    
    data_conclusao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão (para tarefas)")
    concluida = models.BooleanField(default=False, verbose_name="Tarefa Concluída")

    class Meta:
        verbose_name = "Atividade do Cliente"
        verbose_name_plural = "Atividades dos Clientes"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.tipo} para {self.cliente.nome_completo} em {self.data_criacao.strftime('%d/%m/%Y')}"

# NOVO MODELO PARA AS FASES DO FUNIL
class FaseFunil(models.Model):
    """
    Define as fases personalizadas do funil de vendas para cada imobiliária.
    """
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, related_name='fases_funil')
    nome = models.CharField(max_length=50)
    ordem = models.PositiveIntegerField(default=0)
    cor = models.CharField(max_length=7, default='#007bff') # Para personalização visual
    
    class Meta:
        verbose_name = "Fase do Funil"
        verbose_name_plural = "Fases do Funil"
        ordering = ['ordem']
        unique_together = ('imobiliaria', 'nome',)
        
    def __str__(self):
        return f"{self.imobiliaria.nome} - {self.nome}"


# NOVO MODELO PARA O FUNIL DE VENDAS
class Oportunidade(models.Model):
    """
    Representa uma oportunidade de negócio no funil de vendas.
    """
    FONTE_CHOICES = [
        ('SITE', 'Site'),
        ('INDICACAO', 'Indicação'),
        ('ANUNCIO', 'Anúncio Online'),
        ('CLIENTE_ANTIGO', 'Cliente Antigo'),
        ('OUTRO', 'Outro'),
    ]

    titulo = models.CharField(max_length=255, verbose_name="Título da Oportunidade")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="oportunidades", verbose_name="Cliente")
    # CORREÇÃO: Usando string para a ForeignKey para evitar importação circular
    imovel = models.ForeignKey('app_imoveis.Imovel', on_delete=models.SET_NULL, null=True, blank=True, related_name="oportunidades", verbose_name="Imóvel de Interesse") 
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="oportunidades", verbose_name="Corretor Responsável")
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")

    # CAMPO FASE MODIFICADO
    fase = models.ForeignKey(FaseFunil, on_delete=models.SET_NULL, null=True, related_name='oportunidades', verbose_name="Fase do Funil")
    
    valor_estimado = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor Estimado do Negócio")
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateField(null=True, blank=True, verbose_name="Data Prevista de Fechamento")

    fonte = models.CharField(max_length=20, choices=FONTE_CHOICES, null=True, blank=True, verbose_name="Fonte do Lead")
    motivo_perda = models.TextField(null=True, blank=True, verbose_name="Motivo da Perda")
    probabilidade = models.PositiveIntegerField(default=10, verbose_name="Probabilidade de Fechamento (%)")

    class Meta:
        verbose_name = "Oportunidade"
        verbose_name_plural = "Oportunidades"
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo


# NOVO MODELO: Tarefa
class Tarefa(models.Model):
    oportunidade = models.ForeignKey(
        'app_clientes.Oportunidade', 
        on_delete=models.CASCADE, 
        related_name="tarefas", 
        verbose_name="Oportunidade", 
        null=True, 
        blank=True
    )
    descricao = models.TextField(verbose_name="Descrição da Tarefa")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_conclusao = models.DateField(null=True, blank=True, verbose_name="Data de Conclusão")
    concluida = models.BooleanField(default=False, verbose_name="Concluída")
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Responsável")

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ['data_conclusao']

    def __str__(self):
        return f"Tarefa: {self.descricao[:50]}..."
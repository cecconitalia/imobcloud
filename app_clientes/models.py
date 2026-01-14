# app_clientes/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
from django.core.exceptions import ValidationError
import re

User = get_user_model()

# ====================================================================
# FUNÇÃO UTILITÁRIA
# ====================================================================
def apenas_numeros(valor):
    """Remove todos os caracteres não numéricos de uma string."""
    return re.sub(r'[^0-9]', '', str(valor or ''))

# ====================================================================
# MODELO: Etapas do Funil
# ====================================================================

class FunilEtapa(models.Model):
    imobiliaria = models.ForeignKey('core.Imobiliaria', on_delete=models.CASCADE, related_name='etapas_funil')
    titulo = models.CharField(max_length=255)
    ordem = models.IntegerField(default=0)
    probabilidade_fechamento = models.IntegerField(default=0) # Porcentagem
    ativa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Etapa do Funil"
        verbose_name_plural = "Etapas do Funil"
        ordering = ['imobiliaria', 'ordem']
        unique_together = ('imobiliaria', 'titulo')

    def __str__(self):
        return f"{self.imobiliaria.nome} - {self.titulo}"

# ====================================================================
# Modelos do CRM
# ====================================================================

class Cliente(models.Model):
    TIPO_PESSOA_CHOICES = (
        ('FISICA', 'Pessoa Física'),
        ('JURIDICA', 'Pessoa Jurídica'),
    )
    tipo_pessoa = models.CharField(max_length=8, choices=TIPO_PESSOA_CHOICES, default='FISICA', verbose_name="Tipo de Pessoa")
    
    imobiliaria = models.ForeignKey('core.Imobiliaria', on_delete=models.CASCADE, verbose_name="Imobiliária")
    
    documento = models.CharField(max_length=18, verbose_name="CPF/CNPJ")

    nome = models.CharField(max_length=200, verbose_name="Nome Completo / Nome Fantasia")
    rg = models.CharField(max_length=20, blank=True, null=True, verbose_name="RG")
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    estado_civil = models.CharField(max_length=50, blank=True, null=True, verbose_name="Estado Civil")
    profissao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Profissão")

    razao_social = models.CharField(max_length=255, blank=True, null=True, verbose_name="Razão Social")
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True, verbose_name="Inscrição Estadual")

    foto_perfil = models.ImageField(upload_to='clientes_fotos/', blank=True, null=True, verbose_name="Foto de Perfil")
    email = models.EmailField(verbose_name="E-mail", blank=True, null=True)
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    
    logradouro = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro (Rua, Av.)")
    numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    complemento = models.CharField(max_length=255, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")
    
    preferencias_imovel = models.TextField(blank=True, null=True, verbose_name="Preferências de Imóvel")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    perfil_cliente = models.JSONField(
        default=list, 
        blank=True, 
        verbose_name="Perfis do Cliente (Interessado, Proprietário, etc.)",
        help_text="Lista de perfis/funções do cliente."
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    def clean(self):
        super().clean()
        if self.documento:
            self.documento = apenas_numeros(self.documento)
        
        if self.tipo_pessoa == 'FISICA':
            if len(self.documento) != 11:
                raise ValidationError({'documento': 'CPF deve conter 11 dígitos.'})
            self.razao_social = None 
            self.inscricao_estadual = None
        elif self.tipo_pessoa == 'JURIDICA':
            if len(self.documento) != 14:
                raise ValidationError({'documento': 'CNPJ deve conter 14 dígitos.'})
            if not self.razao_social:
                 raise ValidationError({'razao_social': 'Razão Social é obrigatória para Pessoa Jurídica.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        unique_together = ('imobiliaria', 'documento')

    def __str__(self):
        nome_display = self.nome
        if self.tipo_pessoa == 'JURIDICA' and self.razao_social:
            nome_display = self.razao_social
        return f"{nome_display} ({self.imobiliaria.nome})"

class Oportunidade(models.Model):
    class Fases(models.TextChoices):
        LEAD = 'LEAD', 'Novo Lead'
        CONTATO = 'CONTATO', 'Primeiro Contato'
        VISITA = 'VISITA', 'Visita Agendada'
        PROPOSTA = 'PROPOSTA', 'Proposta Enviada'
        NEGOCIACAO = 'NEGOCIACAO', 'Em Negociação'
        GANHO = 'GANHO', 'Negócio Ganho'
        PERDIDO = 'PERDIDO', 'Negócio Perdido'

    class Fontes(models.TextChoices):
        SITE = 'SITE', 'Site'
        INDICACAO = 'INDICACAO', 'Indicação'
        ANUNCIO = 'ANUNCIO', 'Anúncio Online'
        CLIENTE_ANTIGO = 'CLIENTE_ANTIGO', 'Cliente Antigo'
        OUTRO = 'OUTRO', 'Outro'

    imobiliaria = models.ForeignKey('core.Imobiliaria', on_delete=models.CASCADE, related_name='oportunidades')
    imovel = models.ForeignKey('app_imoveis.Imovel', on_delete=models.SET_NULL, null=True, blank=True, related_name='oportunidades')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='oportunidades')

    fase = models.CharField(max_length=20, choices=Fases.choices, default=Fases.LEAD)
    fonte = models.CharField(max_length=20, choices=Fontes.choices, null=True, blank=True, verbose_name="Fonte do Lead")
    
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='oportunidades_responsavel'
    )
    
    titulo = models.CharField(max_length=255, verbose_name="Título da Oportunidade")
    valor_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valor Estimado")
    probabilidade = models.IntegerField(default=10, verbose_name="Probabilidade de Fechamento")
    
    motivo_perda = models.TextField(blank=True, null=True, verbose_name="Motivo da Perda")
    
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    informacoes_adicionais = models.TextField(blank=True, null=True, verbose_name="Informações Adicionais")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Oportunidade de Venda"
        verbose_name_plural = "Oportunidades de Venda"

    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        self.probabilidade = Oportunidade.PROBABILIDADE_POR_FASE.get(self.fase, 0)
        super().save(*args, **kwargs)

    PROBABILIDADE_POR_FASE = {
        Fases.LEAD: 10,
        Fases.CONTATO: 25,
        Fases.VISITA: 50,
        Fases.PROPOSTA: 75,
        Fases.NEGOCIACAO: 90,
        Fases.GANHO: 100,
        Fases.PERDIDO: 0,
    }

class Tarefa(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
    ]

    imobiliaria = models.ForeignKey(
        'core.Imobiliaria', 
        on_delete=models.CASCADE, 
        related_name='tarefas',
        null=True,
        blank=True
    )
    
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    data_vencimento = models.DateTimeField()
    
    # Campo adicionado para corrigir o erro e padronizar
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='MEDIA', verbose_name="Prioridade")
    
    concluida = models.BooleanField(default=False)
    
    oportunidade = models.ForeignKey(
        Oportunidade, 
        on_delete=models.CASCADE, 
        related_name='tarefas', 
        null=True,
        blank=True,
    )
    responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tarefas_responsavel')
    google_calendar_event_id = models.CharField(max_length=255, blank=True, null=True)
    
    observacoes_finalizacao = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Observações da Finalização"
    )

    def __str__(self):
        return f"Tarefa: {self.titulo}"

    def save(self, *args, **kwargs):
        if self.concluida and self.status != 'concluida':
            self.status = 'concluida'
        elif self.status == 'concluida' and not self.concluida:
            self.concluida = True
        elif not self.concluida and self.status == 'concluida':
            self.status = 'pendente'
            
        super().save(*args, **kwargs)

class Visita(models.Model):
    imobiliaria = models.ForeignKey('core.Imobiliaria', on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    
    corretor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='visitas_realizadas',
        verbose_name="Corretor Responsável"
    )
    
    imoveis = models.ManyToManyField('app_imoveis.Imovel', related_name='visitas', verbose_name="Imóveis Visitados")
    
    data_visita = models.DateTimeField()
    observacoes = models.TextField(blank=True, null=True)

    # --- ASSINATURAS ---
    realizada = models.BooleanField(default=False, verbose_name="Visita Realizada")
    localizacao_assinatura = models.CharField(max_length=255, blank=True, null=True, help_text="Lat/Long ou endereço GPS no momento da assinatura")
    
    assinatura_cliente = models.ImageField(upload_to='assinaturas_visitas/', blank=True, null=True, verbose_name="Assinatura do Cliente")
    data_assinatura = models.DateTimeField(blank=True, null=True, verbose_name="Data da Assinatura Cliente")

    assinatura_corretor = models.ImageField(upload_to='assinaturas_visitas/', blank=True, null=True, verbose_name="Assinatura do Corretor")
    data_assinatura_corretor = models.DateTimeField(blank=True, null=True, verbose_name="Data da Assinatura Corretor")

    def __str__(self):
        return f"Visita de {self.cliente} em {self.data_visita}"

class Atividade(models.Model):
    TIPO_ATIVIDADE_CHOICES = [
        ('LIGACAO', 'Ligação'),
        ('EMAIL', 'Email'),
        ('WHATSAPP', 'WhatsApp'),
        ('NOTA', 'Nota'),
        ('MUDANCA_FASE', 'Mudança de Fase')
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='atividades')
    tipo = models.CharField(max_length=20, choices=TIPO_ATIVIDADE_CHOICES)
    descricao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Atividade de {self.cliente.nome} ({self.get_tipo_display()})"
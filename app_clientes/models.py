# C:\wamp64\www\ImobCloud\app_clientes\models.py

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

User = get_user_model()

# ====================================================================
# NOVO MODELO: Etapas do Funil
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
    imobiliaria = models.ForeignKey('core.Imobiliaria', on_delete=models.CASCADE, verbose_name="Imobiliária")
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf_cnpj = models.CharField(max_length=18, unique=False, verbose_name="CPF/CNPJ")
    email = models.EmailField(verbose_name="E-mail")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    preferencias_imovel = models.TextField(blank=True, null=True, verbose_name="Preferências de Imóvel")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    estado_civil = models.CharField(max_length=50, blank=True, null=True, verbose_name="Estado Civil")
    profissao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Profissão")
    rg = models.CharField(max_length=20, blank=True, null=True, verbose_name="RG")

    endereco = models.CharField(max_length=255, blank=True, null=True, verbose_name="Endereço (Rua, Av.)")
    numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")

    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        unique_together = ('imobiliaria', 'cpf_cnpj')

    def __str__(self):
        return f"{self.nome_completo} ({self.imobiliaria.nome})"

class Oportunidade(models.Model):
    # CORREÇÃO AQUI: As fases agora são dinâmicas, mas mantemos o choices para compatibilidade
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

    # A fase agora pode ser um ForeignKey para o novo modelo
    # Para manter a compatibilidade, vamos usar um CharField por enquanto
    # e migrar no futuro.
    fase = models.CharField(max_length=20, choices=Fases.choices, default=Fases.LEAD)

    # NOVO CAMPO: fonte
    fonte = models.CharField(max_length=20, choices=Fontes.choices, null=True, blank=True, verbose_name="Fonte do Lead")
    
    # Campo de responsável agora é um ForeignKey para o User, não para PerfilUsuario
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
        # Lógica para atualizar a probabilidade baseada na fase
        # Será removida quando o funil for 100% dinâmico
        self.probabilidade = Oportunidade.PROBABILIDADE_POR_FASE.get(self.fase, 0)
        super().save(*args, **kwargs)

    # Dicionário auxiliar para a lógica de probabilidade
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
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    data_vencimento = models.DateTimeField()
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
    
    # --- INÍCIO DA ALTERAÇÃO ---
    # Novo campo para guardar as notas de finalização
    observacoes_finalizacao = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Observações da Finalização"
    )
    # --- FIM DA ALTERAÇÃO ---

    def __str__(self):
        return f"Tarefa: {self.titulo}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Visita(models.Model):
    imobiliaria = models.ForeignKey('core.Imobiliaria', on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    imovel = models.ForeignKey('app_imoveis.Imovel', on_delete=models.CASCADE)
    data_visita = models.DateTimeField()
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Visita de {self.cliente} a {self.imovel}"

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
        return f"Atividade de {self.cliente.nome_completo} ({self.get_tipo_display()})"
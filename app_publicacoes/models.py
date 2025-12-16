# C:\wamp64\www\imobcloud\app_publicacoes\models.py

from django.db import models
from core.models import Imobiliaria, PerfilUsuario
from app_imoveis.models import Imovel

class PublicacaoSocial(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='publicacoes_sociais')
    texto_gerado = models.TextField()
    plataforma = models.CharField(max_length=50) # ex: 'facebook', 'instagram'
    sucesso = models.BooleanField(default=False)
    resposta_api = models.JSONField(null=True, blank=True)
    data_publicacao = models.DateTimeField(auto_now_add=True)
    publicado_por = models.ForeignKey(PerfilUsuario, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        status = "Sucesso" if self.sucesso else "Falha"
        return f"Publicação em {self.plataforma} para {self.imovel.codigo_referencia} - {status}"

class PostAgendado(models.Model):
    """
    Representa uma publicação de rede social que foi agendada para o futuro.
    """
    STATUS_CHOICES = [
        ('AGENDADO', 'Agendado'),
        ('PROCESSANDO', 'Processando'), # Adicionado para o novo fluxo
        ('PUBLICADO', 'Publicado com Sucesso'),
        ('ERRO', 'Erro na Publicação'),
    ]

    imovel = models.ForeignKey(
        Imovel,
        on_delete=models.CASCADE,
        related_name='posts_agendados'
    )
    imobiliaria = models.ForeignKey(
        Imobiliaria,
        on_delete=models.CASCADE,
        related_name='posts_agendados_imobiliaria'
    )
    agendado_por = models.ForeignKey(
        PerfilUsuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts_criados'
    )
    texto = models.TextField()
    plataformas = models.JSONField(
        default=list,
        help_text="Lista de plataformas para publicar, ex: ['facebook', 'instagram']"
    )
    imagens_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de IDs das imagens (ImagemImovel) selecionadas para este post."
    )
    data_agendamento = models.DateTimeField()
    status = models.CharField(
        max_length=20, # Aumentado para acomodar PROCESSANDO
        choices=STATUS_CHOICES,
        default='AGENDADO'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_publicacao_real = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data e hora em que a publicação foi efetivamente realizada."
    )
    resultado_publicacao = models.JSONField(
        null=True,
        blank=True,
        help_text="Armazena o resultado (sucesso ou erro) de cada plataforma."
    )

    class Meta:
        ordering = ['data_agendamento']
        verbose_name = "Post Agendado"
        verbose_name_plural = "Posts Agendados"

    def __str__(self):
        return f"Post para '{self.imovel.titulo_anuncio}' agendado para {self.data_agendamento}"
    
class PublicacaoHistorico(models.Model):
    REDE_SOCIAL_CHOICES = [
        ('Facebook', 'Facebook'),
        ('Instagram', 'Instagram'),
        ('TikTok', 'TikTok'),
        ('LinkedIn', 'LinkedIn'),
        ('Outro', 'Outro'),
    ]
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='historico_publicacoes')
    rede_social = models.CharField(max_length=50, choices=REDE_SOCIAL_CHOICES)
    data_publicacao = models.DateTimeField(auto_now_add=True)
    link_publicacao = models.URLField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['-data_publicacao']
        verbose_name = 'Histórico de Publicação'
        verbose_name_plural = 'Histórico de Publicações'

    def __str__(self):
        return f"Publicação de {self.imovel.titulo_anuncio} em {self.rede_social}"
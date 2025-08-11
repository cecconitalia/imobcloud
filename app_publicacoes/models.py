# app_publicacoes/models.py

from django.db import models
from app_imoveis.models import Imovel
from core.models import PerfilUsuario

# Definimos as opções para a plataforma de uma forma organizada
class PlataformaChoices(models.TextChoices):
    INSTAGRAM = 'instagram', 'Instagram'
    FACEBOOK = 'facebook', 'Facebook'

class PublicacaoSocial(models.Model):
    # Ligação para o imóvel que está a ser publicado. Se o imóvel for apagado, a publicação também será.
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='publicacoes')

    # A rede social onde foi publicado (usando as opções que definimos acima).
    plataforma = models.CharField(max_length=20, choices=PlataformaChoices.choices)

    # O texto final que foi gerado pela IA e (possivelmente) editado pelo usuário.
    texto_gerado = models.TextField(help_text="O conteúdo do post gerado pela IA.")

    # Quem foi o usuário que clicou no botão para publicar.
    publicado_por = models.ForeignKey(PerfilUsuario, on_delete=models.SET_NULL, null=True, blank=True)

    # A data e hora em que a publicação foi feita, preenchida automaticamente.
    data_publicacao = models.DateTimeField(auto_now_add=True)

    # Um campo para sabermos se a publicação na rede social realmente funcionou.
    sucesso = models.BooleanField(default=False)

    # Se a publicação for bem-sucedida, guardamos o link para ela (ex: o URL do post no Instagram).
    link_publicacao = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        # Organiza as publicações pela mais recente primeiro no painel de administração.
        ordering = ['-data_publicacao']
        # Garante que não criamos duas publicações idênticas para o mesmo imóvel na mesma plataforma.
        unique_together = ['imovel', 'plataforma', 'texto_gerado']

    def __str__(self):
        # Um texto amigável para identificar a publicação no painel de administração do Django.
        return f"Publicação para '{self.imovel.titulo}' no {self.get_plataforma_display()}"
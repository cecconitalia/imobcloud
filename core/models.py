# C:\wamp64\www\ImobCloud\core\models.py

from django.db import models
from django.conf import settings # Importa settings para User model

class Imobiliaria(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    subdominio = models.CharField(max_length=255, unique=True)
    email_contato = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email para Notificações")

    # Adicione outros campos relevantes para a imobiliária aqui
    # Ex: endereco, telefone, email, logo, etc.

    class Meta:
        verbose_name_plural = "Imobiliárias"

    def __str__(self):
        return self.nome

# MODELO ATUALIZADO: PerfilUsuario
class PerfilUsuario(models.Model):
    # DEFINIÇÃO DOS CARGOS (ROLES)
    class Cargo(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        CORRETOR = 'CORRETOR', 'Corretor'
        
    # Um PerfilUsuario está ligado a um User do Django (relação 1 para 1)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    
    # Um PerfilUsuario pertence a uma Imobiliaria (relação Muitos para Um)
    imobiliaria = models.ForeignKey(
        Imobiliaria,
        on_delete=models.SET_NULL, # Se a imobiliária for deletada, o campo fica NULL
        null=True,
        blank=True, # Permite que o campo seja vazio (para superusuários ou usuários sem imobiliária específica)
        related_name='usuarios_imobiliaria'
    )

    cargo = models.CharField(
        max_length=10,
        choices=Cargo.choices,
        default=Cargo.CORRETOR,
        verbose_name="Cargo"
    )

    # NOVOS CAMPOS ADICIONADOS
    creci = models.CharField(max_length=20, blank=True, null=True, verbose_name="CRECI")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    endereco_logradouro = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    endereco_numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    endereco_bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    endereco_cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    endereco_estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    endereco_cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # NOVO: Campo para o arquivo JSON de credenciais do Google Calendar
    google_json_file = models.FileField(upload_to='google_credentials/', blank=True, null=True, verbose_name="Arquivo de Credenciais do Google")

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return f"Perfil de {self.user.username} ({self.imobiliaria.nome if self.imobiliaria else 'Nenhuma Imobiliária'})"
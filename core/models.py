# C:\wamp64\www\ImobCloud\core\models.py

from django.db import models
from django.conf import settings
from app_config_ia.models import OpcaoVozDaMarca

class Imobiliaria(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    subdominio = models.CharField(max_length=255, unique=True)
    email_contato = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email para Notificações")
    
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name="CNPJ")
    creci = models.CharField(max_length=20, blank=True, null=True, verbose_name="CRECI")

    facebook_page_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID da Página do Facebook")
    facebook_page_access_token = models.CharField(max_length=512, blank=True, null=True, verbose_name="Token de Acesso da Página do Facebook")
    instagram_business_account_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID da Conta Business do Instagram")

    voz_da_marca_preferida = models.ForeignKey(
        OpcaoVozDaMarca,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="A voz da marca que a IA usará para as publicações desta imobiliária."
    )
    
    cor_primaria = models.CharField(
        max_length=7,
        default="#007bff",
        help_text="Cor principal para o site público (código hexadecimal).",
        verbose_name="Cor Principal do Site"
    )

    class Meta:
        verbose_name_plural = "Imobiliárias"

    def __str__(self):
        return self.nome

class PerfilUsuario(models.Model):
    # Removemos a classe Cargo e o campo cargo choices
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    
    imobiliaria = models.ForeignKey(
        Imobiliaria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_imobiliaria'
    )

    # --- NOVOS CAMPOS DE PAPÉIS (Permite múltiplos) ---
    is_admin = models.BooleanField(default=False, verbose_name="É Administrador")
    is_corretor = models.BooleanField(default=True, verbose_name="É Corretor")
    # --------------------------------------------------

    creci = models.CharField(max_length=20, blank=True, null=True, verbose_name="CRECI")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    endereco_logradouro = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    endereco_numero = models.CharField(max_length=10, blank=True, null=True, verbose_name="Número")
    endereco_bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    endereco_cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    endereco_estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    endereco_cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    google_json_file = models.FileField(upload_to='google_credentials/', blank=True, null=True, verbose_name="Arquivo de Credenciais do Google")
    
    google_calendar_token = models.TextField(blank=True, null=True, verbose_name="Token de Acesso do Google Calendar")

    # NOVO CAMPO: Assinatura Digital do Usuário (Corretor)
    assinatura = models.ImageField(
        upload_to='assinaturas_usuarios/', 
        blank=True, 
        null=True, 
        verbose_name="Assinatura Digital",
        help_text="Imagem da assinatura para uso automático em documentos."
    )

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    @property
    def cargo_display(self):
        """Propriedade auxiliar para exibir os cargos numa string (para compatibilidade)"""
        cargos = []
        if self.is_admin:
            cargos.append("Administrador")
        if self.is_corretor:
            cargos.append("Corretor")
        return " / ".join(cargos) if cargos else "Utilizador"

    def __str__(self):
        return f"Perfil de {self.user.username} ({self.cargo_display})"

class Notificacao(models.Model):
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.CharField(max_length=255)
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

    def __str__(self):
        return f"Notificação para {self.destinatario.username}: {self.mensagem}"
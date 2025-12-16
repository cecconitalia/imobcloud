# C:\wamp64\www\imobcloud\core\models.py

from django.db import models
from django.conf import settings
# Importação necessária para criar um modelo de usuário customizado
from django.contrib.auth.models import AbstractUser # <-- CORRIGIDO
from app_config_ia.models import OpcaoVozDaMarca
from django.utils import timezone # Para data_cadastro de Imobiliaria

class Imobiliaria(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    subdominio = models.CharField(max_length=255, unique=True)
    email_contato = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email para Notificações")
    
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name="CNPJ")
    creci = models.CharField(max_length=20, blank=True, null=True, verbose_name="CRECI")

    # CAMPOS FALTANTES ADICIONADOS:
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone de Contato") # <--- ADICIONADO
    facebook_user_access_token = models.CharField(max_length=512, blank=True, null=True, verbose_name="Token de Acesso do Usuário FB") # <--- ADICIONADO
    
    facebook_page_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID da Página do Facebook")
    facebook_page_access_token = models.CharField(max_length=512, blank=True, null=True, verbose_name="Token de Acesso da Página do Facebook")
    instagram_business_account_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID da Conta Business do Instagram")

    # NOVO CAMPO: Chave API do Google Gemini para o Admin configurar
    google_gemini_api_key = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Chave API Google Gemini",
        help_text="Chave de acesso para o serviço Gemini/Google AI."
    )

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
    
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro") # Campo adicionado na migração 0017
    
    class Meta:
        verbose_name_plural = "Imobiliárias"

    def __str__(self):
        return self.nome

# PERFILUSUARIO: MANTIDO COMO ABSTRACTUSER PARA CONSISTÊNCIA APÓS A MIGRAÇÃO 0017
class PerfilUsuario(AbstractUser): 
    # Os campos de autenticação (username, password, email, etc.) são herdados de AbstractUser
    
    imobiliaria = models.ForeignKey(
        'Imobiliaria', # Referência de string para evitar dependência circular
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_imobiliaria'
    )

    is_admin = models.BooleanField(default=False, verbose_name="É Administrador")
    is_corretor = models.BooleanField(default=True, verbose_name="É Corretor")

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

    assinatura = models.ImageField(
        upload_to='assinaturas_usuarios/', 
        blank=True, 
        null=True, 
        verbose_name="Assinatura Digital",
        help_text="Imagem da assinatura para uso automático em documentos."
    )

    class Meta(AbstractUser.Meta): 
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    @property
    def cargo_display(self):
        cargos = []
        if self.is_admin:
            cargos.append("Administrador")
        if self.is_corretor:
            cargos.append("Corretor")
        return " / ".join(cargos) if cargos else "Utilizador"

    def __str__(self):
        return f"Perfil de {self.username} ({self.cargo_display})"

class Notificacao(models.Model):
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField(max_length=100, default='Notificação')
    mensagem = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, default='INFO')
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

    def __str__(self):
        return f"[{self.tipo}] Notificação para {self.destinatario.username}: {self.mensagem}"
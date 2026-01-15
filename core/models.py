# core/models.py

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from app_config_ia.models import OpcaoVozDaMarca
from django.utils import timezone
from datetime import timedelta

# --- NOVO MODELO: CONFIGURAÇÃO GLOBAL (Substitui parte do .env) ---
class ConfiguracaoGlobal(models.Model):
    """
    Armazena configurações do sistema que antes ficavam no .env.
    Padrão Singleton: Só deve haver uma linha nesta tabela.
    """
    # GERAL
    site_url = models.CharField(max_length=255, default="https://imobhome.com.br", verbose_name="URL do Sistema")
    base_public_url = models.CharField(max_length=255, default="https://imobhome.com.br", verbose_name="URL Pública Base")
    
    # EMAIL (SMTP)
    email_host = models.CharField(max_length=255, default="smtp.gmail.com", verbose_name="Host SMTP")
    email_port = models.IntegerField(default=587, verbose_name="Porta SMTP")
    email_host_user = models.CharField(max_length=255, verbose_name="Usuário SMTP (Email)")
    email_host_password = models.CharField(max_length=255, verbose_name="Senha SMTP (App Password)")
    default_from_email = models.CharField(max_length=255, default="ImobHome <noreply@imobhome.com.br>", verbose_name="Remetente Padrão")

    # INTEGRAÇÕES GOOGLE
    google_api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name="Google API Key (Maps/Gemini Global)")

    # CLOUDINARY
    cloudinary_cloud_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cloudinary Cloud Name")
    cloudinary_api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cloudinary API Key")
    cloudinary_api_secret = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cloudinary API Secret")

    # MANUTENÇÃO
    modo_manutencao = models.BooleanField(default=False, verbose_name="Modo Manutenção")

    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"

    def save(self, *args, **kwargs):
        # Garante que só exista ID 1
        self.pk = 1
        super(ConfiguracaoGlobal, self).save(*args, **kwargs)

    def __str__(self):
        return "Configuração Global do Sistema"

# --- MODELO EXISTENTE: PLANO ---
class Plano(models.Model):
    nome = models.CharField(max_length=100, help_text="Ex: Mensal Básico, Anual Pro")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Plano")
    dias_ciclo = models.IntegerField(default=30, help_text="A cada quantos dias vence? (30 = Mensal, 365 = Anual)")
    dias_para_bloqueio = models.IntegerField(
        default=5, 
        help_text="Quantos dias após o vencimento o sistema deve bloquear o acesso? (Ex: 5 dias de tolerância)"
    )
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} - R$ {self.valor}"

class Imobiliaria(models.Model):
    nome = models.CharField(max_length=255, unique=True)
    subdominio = models.CharField(max_length=255, unique=True)
    email_contato = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email para Notificações")
    
    # Identidade Visual
    foto_perfil = models.ImageField(
        upload_to='imobiliarias_logos/', 
        null=True, 
        blank=True, 
        verbose_name="Logo da Imobiliária"
    )
    
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name="CNPJ")
    creci = models.CharField(max_length=20, blank=True, null=True, verbose_name="CRECI")

    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone de Contato")
    facebook_user_access_token = models.CharField(max_length=512, blank=True, null=True, verbose_name="Token de Acesso do Usuário FB")
    
    facebook_page_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID da Página do Facebook")
    facebook_page_access_token = models.CharField(max_length=512, blank=True, null=True, verbose_name="Token de Acesso da Página do Facebook")
    instagram_business_account_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID da Conta Business do Instagram")

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
    
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")

    # --- CAMPOS FINANCEIROS (SAAS) ---
    plano_contratado = models.ForeignKey(Plano, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Plano Atual")
    data_vencimento_atual = models.DateField(null=True, blank=True, verbose_name="Próximo Vencimento")
    
    STATUS_FINANCEIRO_CHOICES = [
        ('ATIVO', 'Ativo (Em dia)'),
        ('PENDENTE', 'Pagamento Pendente (Em tolerância)'),
        ('BLOQUEADO', 'Acesso Bloqueado (Inadimplente)'),
        ('CANCELADO', 'Cancelado'),
        ('GRATIS', 'Período de Teste'),
    ]
    status_financeiro = models.CharField(
        max_length=20, 
        choices=STATUS_FINANCEIRO_CHOICES, 
        default='GRATIS',
        verbose_name="Status da Assinatura"
    )

    def verificar_status_bloqueio(self):
        """
        Lógica automática para verificar vencimento e aplicar bloqueio.
        """
        # Se for teste grátis, verifica os 7 dias
        if self.status_financeiro == 'GRATIS':
            limite_teste = self.data_cadastro + timedelta(days=7)
            if timezone.now() > limite_teste:
                self.status_financeiro = 'BLOQUEADO'
                self.save(update_fields=['status_financeiro'])
            return

        # Se não tem plano ou data de vencimento, e não é grátis, assume bloqueado ou incompleto
        if not self.plano_contratado or not self.data_vencimento_atual:
            return 

        hoje = timezone.now().date()
        dias_atraso = (hoje - self.data_vencimento_atual).days

        # Se dias_atraso > 0, está vencido
        if dias_atraso > 0:
            if dias_atraso <= self.plano_contratado.dias_para_bloqueio:
                # Dentro da tolerância -> PENDENTE
                if self.status_financeiro != 'PENDENTE':
                    self.status_financeiro = 'PENDENTE'
                    self.save(update_fields=['status_financeiro'])
            else:
                # Passou da tolerância -> BLOQUEADO
                if self.status_financeiro != 'BLOQUEADO':
                    self.status_financeiro = 'BLOQUEADO'
                    self.save(update_fields=['status_financeiro'])
        else:
            # Em dia
            if self.status_financeiro in ['PENDENTE', 'BLOQUEADO']:
                self.status_financeiro = 'ATIVO'
                self.save(update_fields=['status_financeiro'])

    class Meta:
        verbose_name_plural = "Imobiliárias"

    def __str__(self):
        return f"{self.nome} ({self.get_status_financeiro_display()})"

class PerfilUsuario(AbstractUser): 
    imobiliaria = models.ForeignKey(
        'Imobiliaria', 
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
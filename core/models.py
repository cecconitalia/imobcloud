import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

# --- NOVO MODELO: CONFIGURAÇÃO GLOBAL ---
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
    email_host_user = models.CharField(max_length=255, blank=True, null=True, verbose_name="Usuário SMTP (Email)")
    email_host_password = models.CharField(max_length=255, blank=True, null=True, verbose_name="Senha SMTP (App Password)")
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
    # Enums para Escolhas
    TIPO_PESSOA_CHOICES = [
        ('PJ', 'Pessoa Jurídica'),
        ('PF', 'Pessoa Física'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVA', 'Ativa'),
        ('SUSPENSA', 'Suspensa'),
        ('INATIVA', 'Inativa'),
    ]

    TIPO_CRECI_CHOICES = [
        ('JURIDICO', 'Jurídico'),
        ('FISICO', 'Físico'),
    ]

    UF_CHOICES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'),
        ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'),
        ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
        ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'),
        ('SE', 'Sergipe'), ('TO', 'Tocantins')
    ]

    # --- 1. IDENTIFICAÇÃO DA IMOBILIÁRIA ---
    
    # UUID: Agora definido como unique=True e obrigatório (sem null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="ID Interno (UUID)")
    
    # Campos legados
    nome = models.CharField(max_length=255, unique=True, verbose_name="Nome (Sistema)")
    subdominio = models.CharField(max_length=255, unique=True, verbose_name="Subdomínio")
    
    # Novos campos de identificação
    nome_fantasia = models.CharField("Nome Fantasia", max_length=255, blank=True, null=True)
    razao_social = models.CharField("Razão Social", max_length=255, blank=True, null=True)
    tipo_pessoa = models.CharField("Tipo de Pessoa", max_length=2, choices=TIPO_PESSOA_CHOICES, default='PJ')
    
    # Unificando CNPJ/CPF em um campo principal
    cnpj_cpf = models.CharField("CNPJ / CPF", max_length=20, blank=True, null=True, unique=True)
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name="CNPJ (Legado)") # Mantido para compatibilidade
    
    inscricao_estadual = models.CharField("Inscrição Estadual", max_length=50, blank=True, null=True)
    inscricao_municipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)
    data_fundacao = models.DateField("Data de Fundação", blank=True, null=True)
    natureza_juridica = models.CharField("Natureza Jurídica", max_length=100, blank=True, null=True)
    cnae_principal = models.CharField("CNAE Principal", max_length=20, blank=True, null=True)
    cnae_secundarios = models.TextField("CNAEs Secundários", blank=True, null=True)
    status = models.CharField("Status da Empresa", max_length=20, choices=STATUS_CHOICES, default='ATIVA')
    
    # Identidade Visual
    foto_perfil = models.ImageField(
        upload_to='imobiliarias_logos/', 
        null=True, 
        blank=True, 
        verbose_name="Logo da Imobiliária (Principal)"
    )
    # Campo legado mantido para compatibilidade
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name="Logo (Legado)")

    # --- 2. DADOS DE CONTATO ---
    email_contato = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email Principal (Notificações)")
    email_financeiro = models.EmailField("E-mail Financeiro", blank=True, null=True)
    email_suporte = models.EmailField("E-mail Suporte", blank=True, null=True)
    
    telefone_fixo = models.CharField("Telefone Fixo", max_length=20, blank=True, null=True)
    # Campo 'telefone' legado mapeado para Celular/Principal
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone (Legado/Celular)")
    telefone_celular = models.CharField("Telefone Celular", max_length=20, blank=True, null=True)
    whatsapp = models.CharField("WhatsApp", max_length=20, blank=True, null=True)
    
    website = models.URLField("Website", blank=True, null=True)
    instagram = models.URLField("Instagram", blank=True, null=True)
    facebook = models.URLField("Facebook", blank=True, null=True)
    linkedin = models.URLField("LinkedIn", blank=True, null=True)
    outros_links = models.TextField("Outros Links Sociais", blank=True, null=True)

    # Redes Sociais (Integração Legada)
    facebook_user_access_token = models.CharField(max_length=512, blank=True, null=True, verbose_name="Token de Acesso do Usuário FB")
    facebook_page_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID da Página do Facebook")
    facebook_app_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID do Aplicativo do Facebook")
    facebook_app_secret = models.CharField(max_length=255, blank=True, null=True, verbose_name="Segredo do Aplicativo do Facebook")
    facebook_page_access_token = models.CharField(max_length=512, blank=True, null=True, verbose_name="Token de Acesso da Página do Facebook")
    instagram_business_account_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID da Conta Business do Instagram")

    # --- 3. ENDEREÇO COMERCIAL ---
    cep = models.CharField("CEP", max_length=10, blank=True, null=True)
    logradouro = models.CharField("Logradouro", max_length=255, blank=True, null=True)
    numero = models.CharField("Número", max_length=20, blank=True, null=True)
    complemento = models.CharField("Complemento", max_length=100, blank=True, null=True)
    bairro = models.CharField("Bairro", max_length=100, blank=True, null=True)
    cidade = models.CharField("Cidade", max_length=100, blank=True, null=True)
    estado = models.CharField("Estado", max_length=2, choices=UF_CHOICES, blank=True, null=True)
    pais = models.CharField("País", max_length=50, default='Brasil', blank=True, null=True)
    regiao_administrativa = models.CharField("Região Administrativa", max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # --- 4. RESPONSÁVEL LEGAL ---
    responsavel_nome = models.CharField("Nome do Responsável", max_length=255, blank=True, null=True)
    responsavel_cpf = models.CharField("CPF do Responsável", max_length=14, blank=True, null=True)
    responsavel_rg = models.CharField("RG do Responsável", max_length=20, blank=True, null=True)
    responsavel_orgao_emissor = models.CharField("Órgão Emissor", max_length=20, blank=True, null=True)
    responsavel_data_nascimento = models.DateField("Data de Nascimento", blank=True, null=True)
    responsavel_cargo = models.CharField("Cargo", max_length=100, blank=True, null=True)
    responsavel_email = models.EmailField("E-mail do Responsável", blank=True, null=True)
    responsavel_telefone = models.CharField("Telefone do Responsável", max_length=20, blank=True, null=True)
    responsavel_whatsapp = models.CharField("WhatsApp do Responsável", max_length=20, blank=True, null=True)
    responsavel_assinatura = models.ImageField("Assinatura Digital", upload_to='imobiliarias/assinaturas/', blank=True, null=True)
    responsavel_documento = models.FileField("Documento de Identificação", upload_to='imobiliarias/documentos/', blank=True, null=True)

    # --- 5. CRECI E REGULAMENTAÇÃO ---
    creci_numero = models.CharField("Número do CRECI", max_length=20, blank=True, null=True)
    # Mantém campo 'creci' legado para compatibilidade
    creci = models.CharField(max_length=20, blank=True, null=True, verbose_name="CRECI (Legado)")
    
    creci_uf = models.CharField("UF do CRECI", max_length=2, choices=UF_CHOICES, blank=True, null=True)
    creci_tipo = models.CharField("Tipo de CRECI", max_length=20, choices=TIPO_CRECI_CHOICES, default='JURIDICO')
    creci_situacao = models.CharField("Situação do CRECI", max_length=50, default='Ativo', blank=True, null=True)
    creci_validade = models.DateField("Validade do CRECI", blank=True, null=True)
    creci_documento = models.FileField("Documento CRECI (Upload)", upload_to='imobiliarias/creci/', blank=True, null=True)
    outros_registros = models.TextField("Outros Registros Profissionais", blank=True, null=True)

    # --- CONFIGURAÇÕES DE SISTEMA ---
    google_gemini_api_key = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Chave API Google Gemini",
        help_text="Chave de acesso para o serviço Gemini/Google AI."
    )

    # Uso de string para evitar Circular Import com app_config_ia
    voz_da_marca_preferida = models.TextField(
        blank=True, 
        null=True, 
        help_text="A voz da marca que a IA usará para as publicações desta imobiliária (Ex: Formal, Casual, Luxuoso)."
    )
    
    cor_primaria = models.CharField(
        max_length=7,
        default="#007bff",
        help_text="Cor principal para o site público (código hexadecimal).",
        verbose_name="Cor Principal do Site"
    )
    
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

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
        verbose_name = "Imobiliária"
        verbose_name_plural = "Imobiliárias"
        ordering = ['nome_fantasia', 'nome']

    def __str__(self):
        # Prioriza Nome Fantasia, depois Razão Social, depois Nome antigo
        nome_display = self.nome_fantasia or self.razao_social or self.nome
        return f"{nome_display} ({self.get_status_financeiro_display()})"

    @property
    def endereco_completo(self):
        """
        Retorna o endereço formatado numa string única.
        Útil para documentos e exibição no frontend.
        """
        partes = []
        if self.logradouro:
            partes.append(self.logradouro)
        if self.numero:
            partes.append(f"nº {self.numero}")
        if self.complemento:
            partes.append(self.complemento)
        if self.bairro:
            partes.append(f"- {self.bairro}")
        if self.cidade and self.estado:
            partes.append(f"{self.cidade}/{self.estado}")
        elif self.cidade:
            partes.append(self.cidade)
        
        if self.cep:
            partes.append(f"CEP: {self.cep}")
            
        return ", ".join(partes)

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
    
    # Campo obrigatório para resolver o erro no Serializer
    foto_perfil = models.ImageField(
        upload_to='usuarios_fotos/', 
        blank=True, 
        null=True, 
        verbose_name="Foto de Perfil"
    )

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
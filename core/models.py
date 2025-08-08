# C:\wamp64\www\ImobCloud\core\models.py (CÓDIGO COMPLETO E ATUALIZADO)

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser # Importação recomendada
from threading import local

# ==============================================================================
# 1. ARQUITETURA MULTI-TENANT (O CÉREBRO DO SISTEMA)
# ==============================================================================

# Objeto para armazenar dados específicos desta requisição (thread).
_thread_locals = local()

def get_current_tenant():
    """
    Função global que permite que qualquer parte do sistema (como os Managers)
    acesse a imobiliária (tenant) da requisição atual.
    """
    return getattr(_thread_locals, 'tenant', None)

class ImobiliariaManager(models.Manager):
    """
    Manager que filtra automaticamente os resultados pela
    imobiliária (tenant) da requisição atual. Essencial para a arquitetura multi-tenant.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        if tenant:
            # Assumimos que o modelo que usa este manager tem um campo 'imobiliaria'
            return qs.filter(imobiliaria=tenant)
        
        # Se nenhum tenant for encontrado (ex: no site público geral ou superuser),
        # retorna uma queryset vazia para evitar vazamento de dados.
        # Você pode mudar para `return qs` se quiser que superusuários vejam tudo.
        return qs.none()


# ==============================================================================
# 2. SEUS MODELOS, AGORA INTEGRADOS À ARQUITETURA
# ==============================================================================

class Imobiliaria(models.Model):
    """
    Representa uma imobiliária (tenant). Este é o modelo central.
    """
    nome = models.CharField(max_length=255, unique=True)
    subdominio = models.CharField(max_length=255, unique=True)
    email_contato = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email para Notificações")

    class Meta:
        verbose_name = "Imobiliária" # Corrigido para singular
        verbose_name_plural = "Imobiliárias"

    def __str__(self):
        return self.nome

class PerfilUsuario(models.Model):
    """
    Perfil do usuário que o conecta a uma imobiliária específica.
    """
    class Cargo(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        CORRETOR = 'CORRETOR', 'Corretor'
        
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    
    # Este campo é a ligação principal do usuário com o tenant.
    imobiliaria = models.ForeignKey(
        Imobiliaria,
        on_delete=models.SET_NULL, # SET_NULL pode ser uma boa opção aqui
        null=True,
        blank=True,
        related_name='perfis_de_usuario' # Nome de related_name mais claro
    )

    cargo = models.CharField(
        max_length=10,
        choices=Cargo.choices,
        default=Cargo.CORRETOR,
        verbose_name="Cargo"
    )

    creci = models.CharField(max_length=20, blank=True, null=True, verbose_name="CRECI")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    # ... outros campos de endereço e observações ...
    
    google_json_file = models.FileField(upload_to='google_credentials/', blank=True, null=True, verbose_name="Arquivo de Credenciais do Google")
    google_calendar_token = models.TextField(blank=True, null=True, verbose_name="Token de Acesso do Google Calendar")

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

    def __str__(self):
        return f"Perfil de {self.user.username} ({self.imobiliaria.nome if self.imobiliaria else 'Nenhuma Imobiliária'})"

class Notificacao(models.Model):
    """
    Notificações para os usuários. Elas também devem pertencer a uma imobiliária
    para que o Manager possa filtrá-las corretamente.
    """
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE)# Adicionado null=True
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.CharField(max_length=255)
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    # Adicionando o Manager para filtro automático
    objects = ImobiliariaManager()

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"

    def __str__(self):
        return f"Notificação para {self.destinatario.username}: {self.mensagem}"
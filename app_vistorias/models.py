from django.db import models
from app_contratos.models import Contrato

class Vistoria(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Vistoria de Entrada'),
        ('SAIDA', 'Vistoria de Saída'),
        ('PERIODICA', 'Vistoria Periódica'),
    ]

    # Vínculo com o Contrato
    contrato = models.ForeignKey(
        Contrato, 
        on_delete=models.CASCADE, 
        related_name='vistorias'
    )
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data_vistoria = models.DateField()
    observacoes = models.TextField(blank=True, null=True)
    
    # Armazena o nome de quem fez (pode ser o usuário logado ou um prestador externo)
    realizado_por_nome = models.CharField(
        max_length=150, 
        blank=True, 
        null=True, 
        help_text="Nome do vistoriador responsável"
    )
    
    # ASSINATURAS DIGITAIS (Dupla)
    # Separei em pastas diferentes para organização
    assinatura_locatario = models.ImageField(upload_to='assinaturas/locatarios/%Y/%m/', blank=True, null=True)
    assinatura_responsavel = models.ImageField(upload_to='assinaturas/responsaveis/%Y/%m/', blank=True, null=True)

    # Controle de sistema
    data_criacao = models.DateTimeField(auto_now_add=True)
    concluida = models.BooleanField(default=False)

    def __str__(self):
        return f"Vistoria #{self.id} - {self.get_tipo_display()}"

class Ambiente(models.Model):
    vistoria = models.ForeignKey(Vistoria, on_delete=models.CASCADE, related_name='ambientes')
    nome = models.CharField(max_length=100) # Ex: Sala, Cozinha, Banheiro Suíte
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nome} (Vistoria #{self.vistoria.id})"

class ItemVistoria(models.Model):
    ESTADO_CHOICES = [
        ('NOVO', 'Novo'),
        ('BOM', 'Bom'),
        ('REGULAR', 'Regular'),
        ('RUIM', 'Ruim'),
        ('INOPERANTE', 'Inoperante/Quebrado'),
    ]

    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE, related_name='itens')
    item = models.CharField(max_length=150) # Ex: Pintura, Piso, Fechadura
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='BOM')
    descricao_avaria = models.TextField(blank=True, null=True, help_text="Descreva detalhes ou avarias")

    def __str__(self):
        return f"{self.item} ({self.estado})"

class VistoriaFoto(models.Model):
    item = models.ForeignKey(ItemVistoria, on_delete=models.CASCADE, related_name='fotos')
    # Renomeado de 'foto' para 'imagem' para padronizar com o serializer
    imagem = models.ImageField(upload_to='vistorias/%Y/%m/')
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto do item {self.item.id}"
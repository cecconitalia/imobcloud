# C:\wamp64\www\ImobCloud\app_boletos\models.py

from django.db import models
from core.models import Imobiliaria
from app_financeiro.models import Transacao
from django.utils import timezone

class ConfiguracaoBanco(models.Model):
    """
    Armazena as credenciais de API de cada banco para uma imobiliária.
    Isso permite que o sistema seja dinâmico e suporte múltiplos bancos.
    """
    BANCO_CHOICES = [
        ('Bradesco', 'Bradesco'),
        ('Itau', 'Itaú'),
        ('Santander', 'Santander'),
        # Adicione outros bancos conforme necessário
    ]
    
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    nome_banco = models.CharField(
        max_length=50, 
        choices=BANCO_CHOICES,
        verbose_name="Banco"
    )
    client_id = models.CharField(max_length=255, verbose_name="Client ID")
    client_secret = models.CharField(max_length=255, verbose_name="Client Secret")
    
    # NOVOS CAMPOS ADICIONADOS
    certificado_file = models.FileField(
        upload_to='bradesco_certs/',
        blank=True,
        null=True,
        verbose_name="Arquivo do Certificado (CRT/PEM)"
    )
    chave_privada_file = models.FileField(
        upload_to='bradesco_certs/',
        blank=True,
        null=True,
        verbose_name="Arquivo da Chave Privada (KEY)"
    )

    class Meta:
        verbose_name = "Configuração do Banco"
        verbose_name_plural = "Configurações dos Bancos"
        unique_together = ('imobiliaria', 'nome_banco')
    
    def __str__(self):
        return f"Configuração {self.nome_banco} para {self.imobiliaria.nome}"

class Boleto(models.Model):
    """
    Representa um boleto gerado para uma transação de receita.
    """
    STATUS_BOLETO_CHOICES = [
        ('EMITIDO', 'Emitido'),
        ('REGISTRADO', 'Registrado'),
        ('PAGO', 'Pago'),
        ('VENCIDO', 'Vencido'),
        ('CANCELADO', 'Cancelado')
    ]
    
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    transacao = models.OneToOneField(
        Transacao, 
        on_delete=models.CASCADE, 
        related_name="boleto",
        verbose_name="Transação Relacionada"
    )
    configuracao = models.ForeignKey(
        ConfiguracaoBanco, 
        on_delete=models.PROTECT,
        verbose_name="Configuração de Banco"
    )

    codigo_barras = models.CharField(max_length=255, verbose_name="Código de Barras")
    linha_digitavel = models.CharField(max_length=255, verbose_name="Linha Digitável")
    url_boleto = models.URLField(max_length=2000, verbose_name="URL do Boleto (PDF)", null=True, blank=True)
    
    status = models.CharField(
        max_length=50, 
        choices=STATUS_BOLETO_CHOICES, 
        default='EMITIDO',
        verbose_name="Status do Boleto"
    )
    
    data_emissao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Emissão")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_pagamento = models.DateField(null=True, blank=True, verbose_name="Data de Pagamento")
    
    class Meta:
        verbose_name = "Boleto"
        verbose_name_plural = "Boletos"
    
    def __str__(self):
        return f"Boleto #{self.id} - {self.transacao.descricao}"
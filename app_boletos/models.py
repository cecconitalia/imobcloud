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
    # CORREÇÃO: Tornando os campos da API opcionais
    client_id = models.CharField(max_length=255, verbose_name="Client ID", blank=True, null=True)
    client_secret = models.CharField(max_length=255, verbose_name="Client Secret", blank=True, null=True)
    
    # NOVOS CAMPOS PARA CNAB
    agencia = models.CharField(max_length=10, help_text="Agência sem o dígito verificador.", default="0000")
    conta = models.CharField(max_length=20, help_text="Número da conta sem o dígito verificador.", default="00000")
    convenio = models.CharField(max_length=20, help_text="Número do convênio ou cedente.", default="0000000")

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

class ArquivoRemessa(models.Model):
    """ Armazena o registro de um arquivo de remessa gerado. """
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE)
    configuracao_banco = models.ForeignKey(ConfiguracaoBanco, on_delete=models.PROTECT)
    data_geracao = models.DateTimeField(auto_now_add=True)
    arquivo = models.FileField(upload_to='remessas/')
    
    class Meta:
        verbose_name = "Arquivo de Remessa"
        verbose_name_plural = "Arquivos de Remessa"
        ordering = ['-data_geracao']

class ArquivoRetorno(models.Model):
    """ Armazena o registro e o conteúdo de um arquivo de retorno processado. """
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE)
    configuracao_banco = models.ForeignKey(ConfiguracaoBanco, on_delete=models.PROTECT)
    data_processamento = models.DateTimeField(auto_now_add=True)
    arquivo = models.FileField(upload_to='retornos/')
    log_processamento = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Arquivo de Retorno"
        verbose_name_plural = "Arquivos de Retorno"
        ordering = ['-data_processamento']

class Boleto(models.Model):
    """
    Representa um boleto individualmente, agora vinculado a uma remessa.
    """
    STATUS_BOLETO_CHOICES = [
        ('PENDENTE', 'Pendente de Remessa'),
        ('ENVIADO', 'Enviado ao Banco'),
        ('PAGO', 'Pago'),
        ('BAIXADO', 'Baixado/Cancelado')
    ]
    
    transacao = models.OneToOneField(Transacao, on_delete=models.CASCADE, related_name="boleto")
    remessa = models.ForeignKey(ArquivoRemessa, on_delete=models.SET_NULL, null=True, blank=True, related_name="boletos")
    retorno = models.ForeignKey(ArquivoRetorno, on_delete=models.SET_NULL, null=True, blank=True, related_name="boletos")
    
    nosso_numero = models.CharField(max_length=20, verbose_name="Nosso Número")
    status = models.CharField(max_length=20, choices=STATUS_BOLETO_CHOICES, default='PENDENTE')
    data_pagamento = models.DateField(null=True, blank=True)
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Boleto para transação #{self.transacao.id} - {self.status}"
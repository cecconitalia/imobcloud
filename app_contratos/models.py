# Em app_contratos/models.py

from django.db import models
from core.models import Imobiliaria
from app_imoveis.models import Imovel
from app_clientes.models import Cliente

class Contrato(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    tipo_contrato = models.CharField(max_length=50, verbose_name="Tipo de Contrato", choices=[('Venda', 'Venda'), ('Aluguel', 'Aluguel')])
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, verbose_name="Imóvel")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Término (se aplicável)")
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Total do Contrato")
    condicoes_pagamento = models.TextField(verbose_name="Condições de Pagamento")
    
    # ## CAMPO ATUALIZADO ##
    # Adicionamos a opção 'Inativo' à lista de escolhas.
    status_contrato = models.CharField(
        max_length=50, 
        default='Ativo', 
        verbose_name="Status do Contrato", 
        choices=[
            ('Ativo', 'Ativo'), 
            ('Concluído', 'Concluído'), 
            ('Rescindido', 'Rescindido'),
            ('Inativo', 'Inativo') # <- OPÇÃO ADICIONADA
        ]
    )
    
    data_assinatura = models.DateField(verbose_name="Data de Assinatura")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ['-data_cadastro']

    def __str__(self):
        return f"Contrato de {self.tipo_contrato} - {self.imovel.endereco} ({self.imobiliaria.nome})"
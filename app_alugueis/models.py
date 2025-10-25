# C:\wamp64\www\imobcloud\app_alugueis\models.py

from django.db import models
from app_imoveis.models import Imovel
from app_contratos.models import Contrato

class Aluguel(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='alugueis')
    contrato = models.OneToOneField(Contrato, on_delete=models.CASCADE, related_name='aluguel')
    data_inicio = models.DateField()
    data_fim = models.DateField()
    valor_mensal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Aluguel"
        verbose_name_plural = "Aluguéis"

    def __str__(self):
        return f"Aluguel do imóvel {self.imovel.titulo_anuncio}"
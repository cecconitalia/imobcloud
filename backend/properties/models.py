# properties/models.py
from django.db import models

class Property(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    address = models.CharField(max_length=255, verbose_name="Endereço")

    # Usamos DecimalField para preços para evitar problemas de arredondamento
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")

    bedrooms = models.PositiveIntegerField(default=0, verbose_name="Quartos")
    bathrooms = models.PositiveIntegerField(default=1, verbose_name="Banheiros")
    area = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Área (m²)")

    is_active = models.BooleanField(default=True, verbose_name="Está Ativo?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Imóvel"
        verbose_name_plural = "Imóveis"
        ordering = ['-created_at']
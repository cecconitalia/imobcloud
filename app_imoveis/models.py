# C:\wamp64\www\ImobCloud\app_imoveis\models.py
from django.db import models
from core.models import Imobiliaria # Importa o modelo Imobiliaria

class Imovel(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    tipo = models.CharField(max_length=50, verbose_name="Tipo de Imóvel") # Ex: "Apartamento", "Casa"
    finalidade = models.CharField(max_length=50, verbose_name="Finalidade", choices=[('Venda', 'Venda'), ('Aluguel', 'Aluguel'), ('Ambos', 'Ambos')])
    endereco = models.CharField(max_length=255, verbose_name="Endereço")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado") # Ex: "SP", "RJ"
    cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")
    valor_venda = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor de Venda")
    valor_aluguel = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor de Aluguel")
    area_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Área Total (m²)")
    area_construida = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Área Construída (m²)")
    quartos = models.IntegerField(default=0, verbose_name="Quartos")
    suites = models.IntegerField(default=0, verbose_name="Suítes")
    banheiros = models.IntegerField(default=0, verbose_name="Banheiros")
    vagas_garagem = models.IntegerField(default=0, verbose_name="Vagas de Garagem")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    status = models.CharField(max_length=50, default='Disponível', verbose_name="Status", choices=[('Disponível', 'Disponível'), ('Alugado', 'Alugado'), ('Vendido', 'Vendido'), ('Em Negociação', 'Em Negociação')])
    aceita_financiamento = models.BooleanField(default=False, verbose_name="Aceita Financiamento")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Imóvel"
        verbose_name_plural = "Imóveis"
        ordering = ['-data_cadastro'] # Ordena os imóveis pelos mais recentes

    def __str__(self):
        return f"{self.tipo} em {self.endereco}, {self.cidade} - {self.imobiliaria.nome}"

class ImagemImovel(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='imagens', verbose_name="Imóvel")
    imagem = models.ImageField(upload_to='imoveis_imagens/', verbose_name="Imagem")
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição da Imagem")
    principal = models.BooleanField(default=False, verbose_name="Imagem Principal")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data de Upload")

    class Meta:
        verbose_name = "Imagem do Imóvel"
        verbose_name_plural = "Imagens dos Imóveis"
        ordering = ['principal', 'data_upload'] # Imagem principal primeiro

    def __str__(self):
        return f"Imagem de {self.imovel.endereco} ({self.imovel.imobiliaria.nome})"
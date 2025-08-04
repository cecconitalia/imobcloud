# C:\wamp64\www\ImobCloud\app_clientes\models.py
from django.db import models
from core.models import Imobiliaria # Importa o modelo Imobiliaria
from app_imoveis.models import Imovel # Importa Imovel para a ForeignKey em Visita

class Cliente(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf_cnpj = models.CharField(max_length=18, unique=False, verbose_name="CPF/CNPJ")
    email = models.EmailField(verbose_name="E-mail")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    preferencias_imovel = models.TextField(blank=True, null=True, verbose_name="Preferências de Imóvel")
    
    # ## CAMPO ADICIONADO ##
    # Este campo irá controlar se o cliente está ativo ou inativo.
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        unique_together = ('imobiliaria', 'cpf_cnpj')

    def __str__(self):
        return f"{self.nome_completo} ({self.imobiliaria.nome})"


class Visita(models.Model):
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, verbose_name="Imóvel")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    data_hora = models.DateTimeField(verbose_name="Data e Hora da Visita")
    status = models.CharField(max_length=50, default='Agendada', verbose_name="Status da Visita", choices=[('Agendada', 'Agendada'), ('Realizada', 'Realizada'), ('Cancelada', 'Cancelada')])
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")

    class Meta:
        verbose_name = "Visita"
        verbose_name_plural = "Visitas"
        ordering = ['data_hora']

    def __str__(self):
        return f"Visita de {self.cliente.nome_completo} a {self.imovel.endereco} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
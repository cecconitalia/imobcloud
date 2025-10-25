from django.db import models

class OpcaoVozDaMarca(models.Model):
    """
    Define os diferentes tons de voz que a IA pode adotar.
    Ex: 'Luxuoso', 'Jovem e Descontraído', 'Técnico'.
    """
    nome = models.CharField(
        max_length=50,
        unique=True,
        help_text="O nome da voz, que será exibido para a imobiliária."
    )
    descricao = models.CharField(
        max_length=255,
        help_text="Uma breve descrição para explicar o estilo desta voz."
    )
    instrucao_ia = models.TextField(
        help_text="Instrução específica para a IA sobre como aplicar esta voz. Ex: 'Use adjetivos sofisticados e foque em exclusividade.'"
    )

    class Meta:
        verbose_name = "Opção de Voz da Marca"
        verbose_name_plural = "Opções de Voz da Marca"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class ModeloDePrompt(models.Model):
    """
    Armazena os templates dos prompts que serão enviados para a IA.
    Permite que o superusuário edite e alterne os prompts sem alterar o código.
    """
    nome_referencia = models.CharField(
        max_length=100,
        unique=True,
        help_text="Um nome interno para identificar este prompt. Ex: 'Post Instagram - Padrão V2'"
    )
    template_do_prompt = models.TextField(
        help_text="O texto do prompt. Use chaves como {{caracteristicas}} para inserir os dados do imóvel."
    )
    em_uso = models.BooleanField(
        default=False,
        help_text="Marque esta opção para que este seja o prompt ativo usado por todo o sistema."
    )
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas internas para o superusuário sobre este prompt."
    )
    
    # NOVO CAMPO: Adicionamos um campo para prompts específicos de busca com IA
    em_uso_busca = models.BooleanField(
        default=False,
        help_text="Marque esta opção para que este seja o prompt ativo para a busca com IA."
    )

    class Meta:
        verbose_name = "Modelo de Prompt da IA"
        verbose_name_plural = "Modelos de Prompt da IA"

    def __str__(self):
        return self.nome_referencia

    def save(self, *args, **kwargs):
        """
        Garante que apenas um prompt possa estar 'em_uso' ou 'em_uso_busca' de cada vez.
        """
        if self.em_uso:
            ModeloDePrompt.objects.filter(em_uso=True).exclude(pk=self.pk).update(em_uso=False)
        if self.em_uso_busca:
            ModeloDePrompt.objects.filter(em_uso_busca=True).exclude(pk=self.pk).update(em_uso_busca=False)
        super(ModeloDePrompt, self).save(*args, **kwargs)
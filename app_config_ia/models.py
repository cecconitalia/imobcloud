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
    # Definição das opções de modelo para aparecer no Admin
    MODELO_CHOICES = [
        ('gemini-1.5-flash', 'Rápido (Gemini 1.5 Flash)'),
        ('gemini-1.5-pro', 'Pro (Gemini 1.5 Pro)'),
        ('gemini-2.0-flash-thinking-exp-01-21', 'Raciocínio (Gemini 2.0 Flash Thinking)'),
    ]

    nome_do_modelo = models.CharField(max_length=100, unique=True, verbose_name="Nome de Identificação")
    
    # Campo novo para selecionar o modelo
    modelo_api = models.CharField(
        max_length=50, 
        choices=MODELO_CHOICES, 
        default='gemini-1.5-flash',
        verbose_name="Modelo de IA",
        help_text="Selecione a inteligência por trás deste prompt."
    )

    template_do_prompt = models.TextField(
        help_text="O texto do prompt. Use {{user_query}} para busca ou {{imovel_data}} para descrição."
    )
    em_uso_busca = models.BooleanField(
        default=False, 
        verbose_name="Em uso para Busca por IA",
        help_text="Marca este prompt como o principal para as buscas no site público."
    )
    em_uso_descricao = models.BooleanField(
        default=False,
        verbose_name="Em uso para Gerar Descrição de Imóvel",
        help_text="Marca este prompt como o principal para gerar descrições no painel."
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Mostra o nome do modelo junto com o nome do prompt na lista
        return f"{self.nome_do_modelo} ({self.get_modelo_api_display()})"

    class Meta:
        verbose_name = "Modelo de Prompt de IA"
        verbose_name_plural = "Modelos de Prompt de IA"
        ordering = ['-data_atualizacao']

    def save(self, *args, **kwargs):
        # Garante que apenas um prompt de CADA tipo esteja ativo
        if self.em_uso_busca:
            ModeloDePrompt.objects.filter(em_uso_busca=True).exclude(pk=self.pk).update(em_uso_busca=False)
        
        if self.em_uso_descricao:
            ModeloDePrompt.objects.filter(em_uso_descricao=True).exclude(pk=self.pk).update(em_uso_descricao=False)

        super(ModeloDePrompt, self).save(*args, **kwargs)
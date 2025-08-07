# C:\wamp64\www\ImobCloud\app_imoveis\models.py
from django.db import models
from core.models import Imobiliaria
from app_clientes.models import Cliente

class Imovel(models.Model):
    # --- CHOICES (Listas de Opções) ---
    class TipoImovel(models.TextChoices):
        CASA = 'CASA', 'Casa'
        APARTAMENTO = 'APARTAMENTO', 'Apartamento'
        TERRENO = 'TERRENO', 'Terreno'
        SALA_COMERCIAL = 'SALA_COMERCIAL', 'Sala Comercial'
        GALPAO = 'GALPAO', 'Galpão'
        RURAL = 'RURAL', 'Rural'
        OUTRO = 'OUTRO', 'Outro'

    class Finalidade(models.TextChoices):
        RESIDENCIAL = 'RESIDENCIAL', 'Residencial'
        COMERCIAL = 'COMERCIAL', 'Comercial'
        INDUSTRIAL = 'INDUSTRIAL', 'Industrial'
        RURAL = 'RURAL', 'Rural'

    class Status(models.TextChoices):
        A_VENDA = 'A_VENDA', 'À Venda'
        PARA_ALUGAR = 'PARA_ALUGAR', 'Para Alugar'
        VENDIDO = 'VENDIDO', 'Vendido'
        ALUGADO = 'ALUGADO', 'Alugado'
        EM_CONSTRUCAO = 'EM_CONSTRUCAO', 'Em Construção'
        DESATIVADO = 'DESATIVADO', 'Desativado'

    class Situacao(models.TextChoices):
        NOVO = 'NOVO', 'Novo'
        USADO = 'USADO', 'Usado'
        NA_PLANTA = 'NA_PLANTA', 'Na Planta'

    class Disponibilidade(models.TextChoices):
        IMEDIATA = 'IMEDIATA', 'Imediata'
        OCUPADO = 'OCUPADO', 'Ocupado'
        DESOCUPADO = 'DESOCUPADO', 'Desocupado'

    class PosicaoSolar(models.TextChoices):
        NORTE = 'NORTE', 'Norte (Sol da Manhã)'
        SUL = 'SUL', 'Sul'
        LESTE = 'LESTE', 'Leste (Sol da Manhã)'
        OESTE = 'OESTE', 'Oeste (Sol da Tarde)'

    class TipoConstrucao(models.TextChoices):
        ALVENARIA = 'ALVENARIA', 'Alvenaria'
        PRE_MOLDADO = 'PRE_MOLDADO', 'Pré-Moldado'
        MISTA = 'MISTA', 'Mista'
        MADEIRA = 'MADEIRA', 'Madeira'
    
    # --- 🏠 Características Gerais ---
    imobiliaria = models.ForeignKey(Imobiliaria, on_delete=models.CASCADE, verbose_name="Imobiliária")
    titulo_anuncio = models.CharField(max_length=255, blank=True, null=True, verbose_name="Título do Anúncio")
    codigo_referencia = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        editable=False, 
        verbose_name="Código de Referência"
    )
    tipo = models.CharField(max_length=50, verbose_name="Tipo de Imóvel", choices=TipoImovel.choices)
    finalidade = models.CharField(max_length=50, verbose_name="Finalidade", choices=Finalidade.choices)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.A_VENDA, verbose_name="Status")
    situacao = models.CharField(max_length=20, choices=Situacao.choices, blank=True, null=True, verbose_name="Situação do Imóvel")
    disponibilidade = models.CharField(max_length=20, choices=Disponibilidade.choices, blank=True, null=True, verbose_name="Disponibilidade")
    
    # --- 💻 Controle de Publicação ---
    publicado_no_site = models.BooleanField(default=True, verbose_name="Publicar no site?")

    # --- 💰 Valores e Taxas ---
    valor_venda = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor de Venda")
    valor_aluguel = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor de Aluguel")
    valor_condominio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valor do Condomínio")
    valor_iptu = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Valor do IPTU (Anual)")
    
    # --- 📍 Localização ---
    endereco = models.CharField(max_length=255, verbose_name="Endereço Completo (Rua, Número)")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado (UF)") 
    cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")
    posicao_solar = models.CharField(max_length=10, choices=PosicaoSolar.choices, blank=True, null=True, verbose_name="Posição Solar")
    andar = models.IntegerField(null=True, blank=True, verbose_name="Andar (se apartamento)")
    vista = models.CharField(max_length=100, blank=True, null=True, verbose_name="Vista (Ex: Mar, Montanha)")
    ponto_referencia = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ponto de Referência")
    localizacao_condominio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Localização no Condomínio")

    # --- 📐 Dimensões e Área ---
    area_construida = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Área Construída (m²)")
    area_util = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Área Útil (m²)")
    area_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Área Total (m²)")
    area_terreno = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Área do Terreno (m²)")
    dimensao_frente = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Frente (m)")
    dimensao_fundos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Fundos (m)")
    dimensao_direita = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Lado Direito (m)")
    dimensao_esquerda = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Lado Esquerdo (m)")

    # --- 🧱 Características Estruturais ---
    ano_construcao = models.IntegerField(null=True, blank=True, verbose_name="Ano de Construção")
    numero_pavimentos = models.IntegerField(default=1, verbose_name="Número de Pavimentos")
    unidades_por_andar = models.IntegerField(null=True, blank=True, verbose_name="Unidades por Andar")
    tipo_construcao = models.CharField(max_length=20, choices=TipoConstrucao.choices, blank=True, null=True, verbose_name="Tipo de Construção")
    pe_direito = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Pé-Direito (m)")

    # --- 🛏️ Divisões Internas ---
    quartos = models.IntegerField(default=0, verbose_name="Quartos")
    suites = models.IntegerField(default=0, verbose_name="Suítes")
    banheiros = models.IntegerField(default=0, verbose_name="Banheiros")
    lavabo = models.BooleanField(default=False, verbose_name="Lavabo")
    sala_estar = models.BooleanField(default=False, verbose_name="Sala de Estar")
    sala_jantar = models.BooleanField(default=False, verbose_name="Sala de Jantar")
    sala_tv = models.BooleanField(default=False, verbose_name="Sala de TV")
    cozinha = models.BooleanField(default=False, verbose_name="Cozinha")
    copa = models.BooleanField(default=False, verbose_name="Copa")
    escritorio = models.BooleanField(default=False, verbose_name="Escritório")
    area_servico = models.BooleanField(default=False, verbose_name="Área de Serviço")
    despensa = models.BooleanField(default=False, verbose_name="Despensa")
    closet = models.BooleanField(default=False, verbose_name="Closet")
    varanda = models.BooleanField(default=False, verbose_name="Varanda / Sacada")
    
    # --- 🚗 Vagas e Garagem ---
    vagas_garagem = models.IntegerField(default=0, verbose_name="Número de Vagas")
    vaga_coberta = models.BooleanField(default=False, verbose_name="Vaga Coberta")
    vaga_privativa = models.BooleanField(default=False, verbose_name="Vaga Privativa")
    portao_eletronico = models.BooleanField(default=False, verbose_name="Portão Eletrônico")

    # --- 🔧 Infraestrutura, Acabamentos e Lazer (Privativo) ---
    ar_condicionado = models.BooleanField(default=False, verbose_name="Ar Condicionado")
    aquecimento = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo de Aquecimento")
    gas_central = models.BooleanField(default=False, verbose_name="Gás Central")
    hidrometro_individual = models.BooleanField(default=False, verbose_name="Hidrômetro Individual")
    piso = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo de Piso")
    moveis_planejados = models.BooleanField(default=False, verbose_name="Móveis Planejados")
    churrasqueira_privativa = models.BooleanField(default=False, verbose_name="Churrasqueira Privativa")
    piscina_privativa = models.BooleanField(default=False, verbose_name="Piscina Privativa")
    
    # --- 🌳 Área Comum / Lazer (Condomínio) ---
    piscina_condominio = models.BooleanField(default=False, verbose_name="Piscina no Condomínio")
    churrasqueira_condominio = models.BooleanField(default=False, verbose_name="Churrasqueira no Condomínio")
    espaco_gourmet = models.BooleanField(default=False, verbose_name="Espaço Gourmet")
    playground = models.BooleanField(default=False, verbose_name="Playground")
    salao_festas = models.BooleanField(default=False, verbose_name="Salão de Festas")
    academia = models.BooleanField(default=False, verbose_name="Academia")
    quadra_esportiva = models.BooleanField(default=False, verbose_name="Quadra Poliesportiva")
    sauna = models.BooleanField(default=False, verbose_name="Sauna")
    espaco_pet = models.BooleanField(default=False, verbose_name="Espaço Pet")

    # --- 🏢 Características do Condomínio ---
    portaria_24h = models.BooleanField(default=False, verbose_name="Portaria 24h")
    elevador = models.BooleanField(default=False, verbose_name="Elevador")
    vagas_visitantes = models.BooleanField(default=False, verbose_name="Vagas para Visitantes")
    bicicletario = models.BooleanField(default=False, verbose_name="Bicicletário")
    
    # --- 📄 Documentação e Autorização de Venda ---
    proprietario = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='imoveis_propriedade', verbose_name="Proprietário")
    numero_matricula = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número da Matrícula do Imóvel")
    data_captacao = models.DateField(null=True, blank=True, verbose_name="Data de Captação / Início da Autorização")
    data_fim_autorizacao = models.DateField(null=True, blank=True, verbose_name="Data de Fim da Autorização")
    possui_exclusividade = models.BooleanField(default=False, verbose_name="Possui Contrato de Exclusividade?")
    comissao_percentual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Comissão Acordada (%)")
    documento_autorizacao = models.FileField(upload_to='autorizacoes/', blank=True, null=True, verbose_name="Documento de Autorização Assinado")
    # NOVO CAMPO ADICIONADO AQUI
    informacoes_adicionais_autorizacao = models.TextField(blank=True, null=True, verbose_name="Informações Adicionais para o Contrato")
    financiavel = models.BooleanField(default=False, verbose_name="Aceita Financiamento")
    aceita_permuta = models.BooleanField(default=False, verbose_name="Aceita Permuta (Troca)")
    quitado = models.BooleanField(default=False, verbose_name="Imóvel Quitado")
    documentacao_ok = models.BooleanField(default=False, verbose_name="Documentação OK")

    # --- 💬 Observações Gerais ---
    descricao_completa = models.TextField(blank=True, null=True, verbose_name="Descrição Detalhada / Observações")
    aceita_pet = models.BooleanField(default=False, verbose_name="Aceita Pet")
    mobiliado = models.BooleanField(default=False, verbose_name="Mobiliado / Semimobiliado")

    # --- Datas de Controle ---
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Imóvel"
        verbose_name_plural = "Imóveis"
        ordering = ['-data_cadastro'] 

    def __str__(self):
        return f"#{self.codigo_referencia} - {self.titulo_anuncio or self.tipo}"

    def save(self, *args, **kwargs):
        if not self.codigo_referencia:
            ultimo_codigo_str = Imovel.objects.all().order_by('-codigo_referencia').values_list('codigo_referencia', flat=True).first()
            ultimo_codigo_int = 0
            if ultimo_codigo_str and ultimo_codigo_str.isdigit():
                ultimo_codigo_int = int(ultimo_codigo_str)

            if ultimo_codigo_int < 1000:
                self.codigo_referencia = "1000"
            else:
                self.codigo_referencia = str(ultimo_codigo_int + 1)
                
        super(Imovel, self).save(*args, **kwargs)


class ImagemImovel(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='imagens', verbose_name="Imóvel")
    imagem = models.ImageField(upload_to='imoveis_imagens/', verbose_name="Imagem")
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição da Imagem")
    principal = models.BooleanField(default=False, verbose_name="Imagem Principal")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data de Upload")

    class Meta:
        verbose_name = "Imagem do Imóvel"
        verbose_name_plural = "Imagens dos Imóveis"
        ordering = ['-principal', '-data_upload'] 

    def __str__(self):
        return f"Imagem de {self.imovel.endereco} ({self.imovel.imobiliaria.nome})"
    
class ContatoImovel(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='contatos', verbose_name="Imóvel")
    nome = models.CharField(max_length=200, verbose_name="Nome do Interessado")
    email = models.EmailField(verbose_name="Email de Contato")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone (Opcional)")
    mensagem = models.TextField(verbose_name="Mensagem")
    data_contato = models.DateTimeField(auto_now_add=True, verbose_name="Data do Contato")
    arquivado = models.BooleanField(default=False, verbose_name="Arquivado")

    class Meta:
        verbose_name = "Contato de Imóvel"
        verbose_name_plural = "Contatos de Imóveis"
        ordering = ['-data_contato']

    def __str__(self):
        return f"Contato de {self.nome} para o imóvel: {self.imovel.endereco}"
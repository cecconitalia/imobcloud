from django.contrib import admin
from .models import Imovel, ImagemImovel, ContatoImovel

# Configuração para exibir imagens inline no admin do Imóvel
class ImagemImovelInline(admin.TabularInline):
    model = ImagemImovel
    extra = 1 # Quantos campos de upload extra mostrar
    ordering = ['ordem'] # Garante a ordem no admin

@admin.register(Imovel)
class ImovelAdmin(admin.ModelAdmin):
    # ATUALIZADO: Melhorado o list_display
    list_display = ('codigo_referencia', 'titulo_anuncio', 'tipo', 'finalidade', 'status', 'valor_venda', 'valor_aluguel', 'imobiliaria', 'publicado_no_site')
    list_editable = ('status', 'publicado_no_site') # Permite edição rápida na lista
    list_filter = ('imobiliaria', 'status', 'tipo', 'cidade', 'finalidade')
    
    # CORREÇÃO DE BUG: Corrigido 'descricao' para 'descricao_completa' e adicionados mais campos úteis
    search_fields = ('logradouro', 'cidade', 'bairro', 'codigo_referencia', 'titulo_anuncio', 'descricao_completa') 
    
    inlines = [ImagemImovelInline] # Adiciona a gestão de imagens dentro do formulário do imóvel

    # Campos que não podem ser editados (como o código de referência)
    readonly_fields = ('codigo_referencia',)

    # NOVO: Adicionados 'fieldsets' para organizar o formulário
    fieldsets = (
        ('🏠 Características Gerais', {
            'fields': ('imobiliaria', 'titulo_anuncio', 'codigo_referencia', 'tipo', 'finalidade', 'status', 'situacao', 'disponibilidade', 'posicao_chave')
        }),
        ('💻 Controle de Publicação', {
            'fields': ('publicado_no_site', 'configuracao_publica')
        }),
        ('💰 Valores e Taxas', {
            'fields': ('valor_venda', 'valor_aluguel', 'valor_condominio', 'valor_iptu')
        }),
        ('📍 Localização', {
            'fields': ('logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'cep', 'posicao_solar', 'andar', 'vista', 'ponto_referencia', 'localizacao_condominio')
        }),
        ('📐 Dimensões e Área', {
            'fields': ('area_construida', 'area_util', 'area_total', 'area_terreno', ('dimensao_frente', 'dimensao_fundos'), ('dimensao_direita', 'dimensao_esquerda'))
        }),
        ('🧱 Características Estruturais', {
            'fields': ('ano_construcao', 'numero_pavimentos', 'unidades_por_andar', 'tipo_construcao', 'pe_direito')
        }),
        ('🛏️ Divisões Internas', {
            # Agrupando campos booleanos na mesma linha
            'fields': (('quartos', 'suites', 'banheiros', 'lavabo'), 
                       ('sala_estar', 'sala_jantar', 'sala_tv'), 
                       ('cozinha', 'copa', 'area_servico'), 
                       ('escritorio', 'despensa', 'closet', 'varanda'))
        }),
        ('🚗 Vagas e Garagem', {
            'fields': ('vagas_garagem', 'vaga_coberta', 'vaga_privativa', 'portao_eletronico')
        }),
        ('🔧 Infraestrutura e Acabamentos (Privativo)', {
            'fields': ('ar_condicionado', 'aquecimento', 'gas_central', 'hidrometro_individual', 'piso', 'moveis_planejados', 'churrasqueira_privativa', 'piscina_privativa')
        }),
        ('🌳 Área Comum / Lazer (Condomínio)', {
            'fields': ('piscina_condominio', 'churrasqueira_condominio', 'espaco_gourmet', 'playground', 'salao_festas', 'academia', 'quadra_esportiva', 'sauna', 'espaco_pet')
        }),
        ('🏢 Características do Condomínio', {
            'fields': ('portaria_24h', 'elevador', 'vagas_visitantes', 'bicicletario')
        }),
        ('📄 Documentação e Captação', {
            'classes': ('collapse',), # Esta secção começa fechada
            'fields': ('proprietario', 'numero_matricula', 'data_captacao', 'data_fim_autorizacao', 'possui_exclusividade', 'comissao_percentual', 'documento_autorizacao', 'informacoes_adicionais_autorizacao', ('financiavel', 'aceita_permuta', 'quitado', 'documentacao_ok'))
        }),
        ('💬 Observações Gerais (AQUI ESTÁ A DESCRIÇÃO)', {
            # 'classes': ('collapse',), # Deixei aberto para facilitar
            'fields': ('descricao_completa', 'outras_caracteristicas', 'aceita_pet', 'mobiliado')
        }),
    )


# NOVA CLASSE ADICIONADA PARA GERIR OS CONTACTOS
@admin.register(ContatoImovel)
class ContatoImovelAdmin(admin.ModelAdmin):
    list_display = ('imovel', 'nome', 'email', 'data_contato', 'arquivado')
    list_filter = ('data_contato', 'imovel', 'arquivado')
    search_fields = ('nome', 'email', 'mensagem')
    # ATUALIZADO
    readonly_fields = ('imovel', 'nome', 'email', 'telefone', 'mensagem', 'data_contato')

    def has_add_permission(self, request):
        # Impede a criação de novos contatos através do painel de admin
        return False
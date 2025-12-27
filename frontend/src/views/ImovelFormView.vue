<template>
  <div class="page-container">
    
    <header class="page-header">
      <div class="header-main">
        <div class="title-area">
           <nav class="breadcrumb">
              <router-link to="/">Início</router-link>
              <i class="fas fa-chevron-right separator"></i> 
              <router-link to="/imoveis">Imóveis</router-link>
              <i class="fas fa-chevron-right separator"></i>
              <span class="active">{{ isEditing ? 'Editar Imóvel' : 'Novo Imóvel' }}</span>
           </nav>
           
           <h1>{{ isEditing ? 'Editar Imóvel' : 'Cadastrar Novo Imóvel' }}</h1>
        </div>
      </div>
    </header>

    <div v-if="isLoadingData" class="loading-state">
         <div class="spinner"></div>
         <p>A carregar dados do imóvel...</p>
    </div>

    <form v-else @submit.prevent="handleSaveAndExit" class="main-content-grid">
      
      <div class="left-column">
        <div class="card form-card no-padding-body">
            
            <div class="tabs-header">
                <button type="button" @click="activeTab = 'geral'" :class="{ active: activeTab === 'geral' }">
                    <i class="fas fa-info-circle"></i> Dados Básicos
                </button>
                <button type="button" @click="activeTab = 'valores'" :class="{ active: activeTab === 'valores' }">
                    <i class="fas fa-dollar-sign"></i> Valores
                </button>
                <button type="button" @click="activeTab = 'caracteristicas'" :class="{ active: activeTab === 'caracteristicas' }">
                    <i class="fas fa-list"></i> Detalhes
                </button>
                <button type="button" @click="activeTab = 'imagens'" :class="{ active: activeTab === 'imagens' }" :disabled="!isEditing">
                    <i class="fas fa-camera"></i> Imagens
                </button>
                <button type="button" @click="activeTab = 'autorizacao'" :class="{ active: activeTab === 'autorizacao' }">
                    <i class="fas fa-file-signature"></i> Autorização
                </button>
                <button type="button" @click="activeTab = 'publico'" :class="{ active: activeTab === 'publico' }">
                    <i class="fas fa-globe"></i> Site
                </button>
            </div>

            <div class="tab-content-area">
                
                <div v-show="activeTab === 'geral'" class="tab-pane fade-in">
                    <div class="form-section compact-section">
                        <div class="form-group full-width">
                            <label>Título do Anúncio <span class="required">*</span></label>
                            <div class="input-wrapper">
                                <i class="fas fa-heading input-icon"></i>
                                <input type="text" v-model="imovel.titulo_anuncio" required class="form-input has-icon" placeholder="Ex: Apartamento Vista Mar no Centro" />
                            </div>
                        </div>

                        <h3 class="section-divider">Localização</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label>CEP</label>
                                <div class="input-wrapper">
                                    <i class="fas fa-map-marker-alt input-icon"></i>
                                    <input type="text" v-model="imovel.cep" class="form-input has-icon" placeholder="00000-000" />
                                </div>
                            </div>
                            <div class="form-group full-width">
                                <label>Logradouro <span class="required">*</span></label>
                                <input type="text" v-model="imovel.logradouro" required class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Número</label>
                                <input type="text" v-model="imovel.numero" class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Complemento</label>
                                <input type="text" v-model="imovel.complemento" class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Bairro <span class="required">*</span></label>
                                <input type="text" v-model="imovel.bairro" required class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Cidade <span class="required">*</span></label>
                                <input type="text" v-model="imovel.cidade" required class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Estado (UF) <span class="required">*</span></label>
                                <input type="text" v-model="imovel.estado" maxlength="2" required class="form-input" style="text-transform: uppercase;" />
                            </div>
                        </div>
                    </div>
                </div>

                <div v-show="activeTab === 'valores'" class="tab-pane fade-in">
                    <div class="form-section compact-section">
                        <h3 class="section-divider">Financeiro</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Valor de Venda</label>
                                <MoneyInput v-model="imovel.valor_venda" class="form-input" :prefix="'R$ '" />
                            </div>
                            <div class="form-group">
                                <label>Valor de Aluguel</label>
                                <MoneyInput v-model="imovel.valor_aluguel" class="form-input" :prefix="'R$ '" />
                            </div>
                            <div class="form-group">
                                <label>Condomínio</label>
                                <MoneyInput v-model="imovel.valor_condominio" class="form-input" :prefix="'R$ '" />
                            </div>
                            <div class="form-group">
                                <label>IPTU (Anual)</label>
                                <MoneyInput v-model="imovel.valor_iptu" class="form-input" :prefix="'R$ '" />
                            </div>
                        </div>

                        <h3 class="section-divider">Medidas e Divisões</h3>
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Área Total (m²)</label>
                                <input type="number" step="0.01" v-model.number="imovel.area_total" class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Área Útil (m²)</label>
                                <input type="number" step="0.01" v-model.number="imovel.area_util" class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Quartos</label>
                                <input type="number" v-model.number="imovel.quartos" class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Suítes</label>
                                <input type="number" v-model.number="imovel.suites" class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Banheiros</label>
                                <input type="number" v-model.number="imovel.banheiros" class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Vagas Garagem</label>
                                <input type="number" v-model.number="imovel.vagas_garagem" class="form-input" />
                            </div>
                        </div>
                    </div>
                </div>

                <div v-show="activeTab === 'caracteristicas'" class="tab-pane fade-in">
                    <div class="form-section compact-section">
                        <h3 class="section-divider">Comodidades do Imóvel</h3>
                        <div class="checkbox-grid">
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.lavabo"><span>Lavabo</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.escritorio"><span>Escritório</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.varanda"><span>Varanda / Sacada</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.mobiliado"><span>Mobiliado</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.ar_condicionado"><span>Ar Condicionado</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.moveis_planejados"><span>Móveis Planejados</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.piscina_privativa"><span>Piscina Privativa</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.churrasqueira_privativa"><span>Churrasqueira</span></label>
                        </div>

                        <h3 class="section-divider">Infraestrutura do Condomínio</h3>
                        <div class="checkbox-grid">
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.portaria_24h"><span>Portaria 24h</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.elevador"><span>Elevador</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.piscina_condominio"><span>Piscina</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.academia"><span>Academia</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.salao_festas"><span>Salão de Festas</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.playground"><span>Playground</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.quadra_esportiva"><span>Quadra Esportiva</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.espaco_pet"><span>Espaço Pet</span></label>
                        </div>

                        <h3 class="section-divider">Descrição e Observações</h3>
                        <div class="form-group full-width">
                            <div class="label-with-action">
                                <label>Descrição Completa (Site)</label>
                                <button type="button" @click.prevent="handleGerarDescricaoIA" 
                                        :disabled="isGerandoDescricao || !isEditing" 
                                        class="btn-text-action">
                                    <i :class="isGerandoDescricao ? 'fas fa-spinner fa-spin' : 'fas fa-magic'"></i>
                                    {{ isGerandoDescricao ? 'Gerando...' : 'Gerar com IA' }}
                                </button>
                            </div>
                            <textarea v-model="imovel.descricao_completa" rows="6" class="form-textarea"></textarea>
                        </div>
                        <div class="form-group full-width">
                            <label>Outras Características</label>
                            <textarea v-model="imovel.outras_caracteristicas" rows="3" class="form-textarea"></textarea>
                        </div>
                    </div>
                </div>

                <div v-show="activeTab === 'imagens'" class="tab-pane fade-in">
                    <div v-if="isEditing && imovel.id">
                        <ImovelImagensView :imovel-id="Number(imovel.id)" />
                    </div>
                    <div v-else class="empty-tab-state">
                        <i class="fas fa-save"></i>
                        <h3>Salve o imóvel primeiro</h3>
                        <p>Você precisa salvar os dados básicos antes de fazer upload das imagens.</p>
                    </div>
                </div>

                <div v-show="activeTab === 'autorizacao'" class="tab-pane fade-in">
                    <div class="form-section compact-section">
                        <div class="form-group full-width">
                            <label>Proprietário <span class="required">*</span></label>
                            <div class="search-input-wrapper">
                                <input 
                                    type="text" 
                                    v-model="searchQuery" 
                                    @input="debouncedSearch($event.target.value)"
                                    placeholder="Buscar proprietário por nome, email ou CPF..."
                                    class="form-input"
                                    autocomplete="off"
                                    :disabled="isLoadingData || isSearchingProprietario"
                                />
                                <i class="fas fa-search search-icon" v-if="!isSearchingProprietario"></i>
                                <i class="fas fa-spinner fa-spin search-icon" v-else></i>
                                
                                <ul v-if="searchQuery && proprietarioSearchResults.length" class="dropdown-results">
                                    <li v-for="cliente in proprietarioSearchResults" 
                                        :key="cliente.id"
                                        @click="selectProprietario(cliente)">
                                        <div class="result-name">{{ cliente.nome || cliente.razao_social }}</div>
                                        <div class="result-sub">{{ cliente.documento }} - {{ cliente.email }}</div>
                                    </li>
                                </ul>
                            </div>
                            
                            <div v-if="proprietarioNomeSelecionado" class="selected-badge">
                                <div class="badge-content">
                                    <i class="fas fa-user-check"></i>
                                    <span>{{ proprietarioNomeSelecionado }}</span>
                                </div>
                                <button type="button" @click="clearProprietarioSelection" class="btn-close-badge" title="Remover"><i class="fas fa-times"></i></button>
                            </div>
                        </div>

                        <div class="form-grid">
                            <div class="form-group">
                                <label>Matrícula</label>
                                <input type="text" v-model="imovel.numero_matricula" class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Comissão (%)</label>
                                <MoneyInput v-model="imovel.comissao_percentual" :suffix="'%'" :precision="2" class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Data Captação</label>
                                <input type="date" v-model="imovel.data_captacao" class="form-input" />
                            </div>
                            <div class="form-group">
                                <label>Fim Autorização</label>
                                <input type="date" v-model="imovel.data_fim_autorizacao" class="form-input" />
                            </div>
                        </div>

                        <h3 class="section-divider">Status da Documentação</h3>
                        <div class="checkbox-grid">
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.possui_exclusividade"><span>Contrato de Exclusividade</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.financiavel"><span>Aceita Financiamento</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.quitado"><span>Quitado</span></label>
                            <label class="custom-checkbox"><input type="checkbox" v-model="imovel.documentacao_ok"><span>Documentação OK</span></label>
                        </div>

                        <div class="form-group full-width" style="margin-top: 1.5rem;">
                            <label>Obs. Contratuais</label>
                            <textarea v-model="imovel.informacoes_adicionais_autorizacao" rows="3" class="form-textarea" placeholder="Informações internas sobre a autorização..."></textarea>
                        </div>
                        
                        <div class="form-group full-width" v-if="isEditing && imovel.id">
                            <button type="button" @click="gerarContratoPDF" class="btn-secondary full-btn">
                                <i class="fas fa-file-pdf"></i> Gerar Contrato de Autorização
                            </button>
                        </div>
                    </div>
                </div>

                <div v-show="activeTab === 'publico'" class="tab-pane fade-in">
                    <div class="alert-box">
                        <i class="fas fa-info-circle"></i>
                        <p>Controle quais campos aparecem publicamente no site da imobiliária.</p>
                    </div>
                    
                    <div v-for="(campos, categoria) in camposVisiveis" :key="categoria" class="visibility-section">
                        <h4 class="visibility-title">{{ categoria }}</h4>
                        <div class="checkbox-grid dense">
                            <label v-for="(label, key) in campos" :key="key" class="custom-checkbox small">
                                <input type="checkbox" :id="key" v-model="imovel.configuracao_publica[key]">
                                <span>{{ label }}</span>
                            </label>
                        </div>
                    </div>
                </div>

            </div>

            <div class="form-footer">
                <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
                <div class="right-actions">
                    <button type="button" @click="handleSaveAndContinue" class="btn-outline-primary" :disabled="isSubmitting">
                        <i class="fas fa-save"></i> Salvar e Continuar
                    </button>
                    <button type="submit" class="btn-primary" :disabled="isSubmitting">
                        <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
                        <span v-else>Salvar e Sair</span>
                    </button>
                </div>
            </div>
        </div>
      </div> 
      
      <div class="right-column">
            
            <div class="card info-card">
                 <div class="widget-header">
                     <h3 class="widget-title"><i class="fas fa-cog"></i> Configurações</h3>
                 </div>
                 
                 <div class="form-group">
                    <label>Tipo de Imóvel</label>
                    <div class="input-wrapper">
                        <select v-model="imovel.tipo" class="form-select">
                            <option value="CASA">Casa</option>
                            <option value="APARTAMENTO">Apartamento</option>
                            <option value="TERRENO">Terreno</option>
                            <option value="SALA_COMERCIAL">Sala Comercial</option>
                            <option value="GALPAO">Galpão</option>
                            <option value="RURAL">Rural</option>
                            <option value="OUTRO">Outro</option>
                        </select>
                    </div>
                 </div>

                 <div class="form-group">
                    <label>Finalidade</label>
                    <select v-model="imovel.finalidade" class="form-select">
                        <option value="RESIDENCIAL">Residencial</option>
                        <option value="COMERCIAL">Comercial</option>
                        <option value="INDUSTRIAL">Industrial</option>
                        <option value="RURAL">Rural</option>
                    </select>
                 </div>

                 <div class="form-group">
                    <label>Situação</label>
                    <select v-model="imovel.situacao" class="form-select">
                        <option :value="null">Não informado</option>
                        <option value="NOVO">Novo</option>
                        <option value="USADO">Usado</option>
                        <option value="NA_PLANTA">Na Planta</option>
                    </select>
                 </div>

                 <div class="form-group">
                    <label>Status Atual</label>
                    <select v-model="imovel.status" class="form-select status-select">
                        <option value="A_VENDA">À Venda</option>
                        <option value="PARA_ALUGAR">Para Alugar</option>
                        <option value="VENDIDO">Vendido</option>
                        <option value="ALUGADO">Alugado</option>
                        <option value="EM_CONSTRUCAO">Em Construção</option>
                        <option value="DESATIVADO">Desativado</option>
                    </select>
                 </div>
            </div>

            <div class="card info-card">
                 <div class="widget-header">
                     <h3 class="widget-title"><i class="fas fa-globe"></i> Visibilidade</h3>
                 </div>
                 <div class="status-toggle-wrapper">
                    <label class="switch-container">
                        <input type="checkbox" v-model="imovel.publicado_no_site">
                        <span class="slider round"></span>
                    </label>
                    <span class="status-label" :class="{ 'text-success': imovel.publicado_no_site, 'text-muted': !imovel.publicado_no_site }">
                        {{ imovel.publicado_no_site ? 'Publicado' : 'Oculto' }}
                    </span>
                 </div>
                 <p class="helper-text-widget">Se desativado, o imóvel não aparecerá no site, independente das outras configurações.</p>
            </div>

      </div> 

    </form>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api'; 
import ImovelImagensView from './ImovelImagensView.vue';
import { debounce } from 'lodash'; 
import '@fortawesome/fontawesome-free/css/all.css';
import MoneyInput from '@/components/MoneyInput.vue';

const route = useRoute();
const router = useRouter();

const imovelId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!imovelId.value);
const activeTab = ref('geral');

const isLoadingData = ref(false);
const isSubmitting = ref(false);
const isGerandoDescricao = ref(false); 

const proprietarioSearchResults = ref<any[]>([]);
const searchQuery = ref('');
const isSearchingProprietario = ref(false);

const proprietarioNomeSelecionado = computed(() => {
    if (imovel.value && imovel.value.proprietario_detalhes) {
        return imovel.value.proprietario_detalhes.nome || imovel.value.proprietario_detalhes.razao_social;
    }
    return null;
});

const camposVisiveis = {
    'Geral': {
        'titulo_anuncio': 'Título', 'tipo': 'Tipo', 'finalidade': 'Finalidade', 'status': 'Status',
    },
    'Financeiro': {
        'valor_venda': 'Valor Venda', 'valor_aluguel': 'Valor Aluguel', 'valor_condominio': 'Condomínio', 'valor_iptu': 'IPTU',
    },
    'Localização': {
        'logradouro': 'Logradouro', 'numero': 'Número', 'bairro': 'Bairro', 'cidade': 'Cidade',
    },
    'Dimensões': {
        'area_util': 'Área Útil', 'area_total': 'Área Total', 'quartos': 'Quartos', 'suites': 'Suítes', 'vagas_garagem': 'Vagas',
    },
    'Detalhes': {
        'descricao_completa': 'Descrição', 'piscina_privativa': 'Piscina', 'churrasqueira_privativa': 'Churrasqueira', 'portaria_24h': 'Portaria 24h', 'elevador': 'Elevador', 'aceita_pet': 'Aceita Pet'
    },
};

const createEmptyImovel = () => {
    const allPublicKeys = Object.values(camposVisiveis).flatMap(obj => Object.keys(obj));
    const defaultConfig = allPublicKeys.reduce((acc, key) => { acc[key] = true; return acc; }, {} as { [key: string]: boolean });

    return {
        id: null,
        titulo_anuncio: '',
        codigo_referencia: '',
        tipo: 'CASA',
        finalidade: 'RESIDENCIAL',
        status: 'A_VENDA',
        situacao: null,
        publicado_no_site: true,
        valor_venda: null as number | null,
        valor_aluguel: null as number | null,
        valor_condominio: null as number | null,
        valor_iptu: null as number | null,
        logradouro: '', numero: '', complemento: '', bairro: '', cidade: '', estado: '', cep: '',
        quartos: 0, suites: 0, banheiros: 0, vagas_garagem: 0, area_total: 0, area_util: 0,
        lavabo: false, escritorio: false, varanda: false, mobiliado: false, ar_condicionado: false,
        moveis_planejados: false, piscina_privativa: false, churrasqueira_privativa: false,
        portaria_24h: false, elevador: false, piscina_condominio: false, academia: false,
        salao_festas: false, playground: false, quadra_esportiva: false, espaco_pet: false,
        financiavel: false, quitado: false, documentacao_ok: false, aceita_pet: false,
        proprietario: null,
        numero_matricula: '', data_captacao: null, data_fim_autorizacao: null, possui_exclusividade: false,
        comissao_percentual: null as number | null,
        informacoes_adicionais_autorizacao: '',
        outras_caracteristicas: '', descricao_completa: '', 
        configuracao_publica: defaultConfig,
        proprietario_detalhes: null as any 
    };
};

const imovel = ref(createEmptyImovel());

const parseToNumber = (value: any): number | null => {
    if (value === null || value === undefined || value === '') return null;
    const num = Number(value);
    return isNaN(num) ? null : num;
};

async function fetchImovelData(id: string) {
  if (!id) return; 
  isLoadingData.value = true;
  try {
    const { data } = await apiClient.get(`/v1/imoveis/${id}/`);
    const emptyImovel = createEmptyImovel();
    
    imovel.value = { 
      ...emptyImovel,
      ...data,
      valor_venda: parseToNumber(data.valor_venda),
      valor_aluguel: parseToNumber(data.valor_aluguel),
      valor_condominio: parseToNumber(data.valor_condominio),
      valor_iptu: parseToNumber(data.valor_iptu),
      comissao_percentual: parseToNumber(data.comissao_percentual),
      proprietario: data.proprietario_detalhes?.id || null, 
      proprietario_detalhes: data.proprietario_detalhes || null, 
      configuracao_publica: { ...emptyImovel.configuracao_publica, ...data.configuracao_publica }
    };
  } catch (error) { console.error(error); } finally { isLoadingData.value = false; }
}

const searchProprietarios = async (query: string) => {
    if (!query || query.length < 3) { proprietarioSearchResults.value = []; return; }
    isSearchingProprietario.value = true;
    try {
        const response = await apiClient.get('/v1/clientes/', { params: { search: query, status: 'ativo' } });
        proprietarioSearchResults.value = response.data; // Removido filtro de tipo para permitir qualquer cliente ser proprietário se necessário, ou manter backend filtering
    } catch (error) { console.error(error); } finally { isSearchingProprietario.value = false; }
};
const debouncedSearch = debounce(searchProprietarios, 300); 

function selectProprietario(cliente: any) {
    imovel.value.proprietario = cliente.id; 
    imovel.value.proprietario_detalhes = cliente; 
    proprietarioSearchResults.value = []; searchQuery.value = ''; 
}
function clearProprietarioSelection() { imovel.value.proprietario = null; imovel.value.proprietario_detalhes = null; }

async function gerarContratoPDF() {
    if (!imovel.value.id || !imovel.value.proprietario) {
         alert("Selecione um 'Proprietário' para gerar o contrato."); return;
    }
    try {
        const payload = {
            comissao_percentual: imovel.value.comissao_percentual,
            data_fim_autorizacao: imovel.value.data_fim_autorizacao,
            informacoes_adicionais: imovel.value.informacoes_adicionais_autorizacao,
        };
        const response = await apiClient.post(`/v1/imoveis/${imovel.value.id}/gerar-autorizacao-pdf/`, payload, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a'); link.href = url;
        link.setAttribute('download', `autorizacao_${imovel.value.codigo_referencia}.pdf`);
        document.body.appendChild(link); link.click(); link.remove(); window.URL.revokeObjectURL(url);
    } catch (error) { console.error(error); alert('Erro ao gerar PDF.'); }
}

async function handleGerarDescricaoIA() {
    if (!isEditing.value || !imovel.value.id) { alert("Salve o imóvel antes."); return; }
    isGerandoDescricao.value = true;
    try {
        const response = await apiClient.post(`/v1/imoveis/${imovel.value.id}/gerar-descricao-ia/`);
        if (response.data?.descricao) { imovel.value.descricao_completa = response.data.descricao; alert("Gerado!"); }
    } catch (error: any) { alert(`Erro: ${error.response?.data?.error || 'Desconhecido'}`); } finally { isGerandoDescricao.value = false; }
}

async function saveImovel() {
  isSubmitting.value = true;
  const payload = { ...imovel.value };
  delete payload.id; delete payload.proprietario_detalhes; 
  Object.keys(payload).forEach(key => { if (key !== 'proprietario' && (payload[key] === null || payload[key] === undefined)) delete payload[key]; });
  
  try {
    if (isEditing.value) return await apiClient.put(`/v1/imoveis/${imovelId.value}/`, payload);
    else return await apiClient.post('/v1/imoveis/', payload);
  } catch (error: any) {
    console.error(error);
    alert('Erro ao salvar. Verifique os campos.');
    return null;
  } finally { isSubmitting.value = false; }
}

async function handleSaveAndExit() {
  const response = await saveImovel();
  if (response?.data) router.push({ name: 'imoveis' });
}

async function handleSaveAndContinue() {
  const response = await saveImovel();
  if (response?.data) {
    const wasCreating = !isEditing.value;
    imovel.value.id = response.data.id;
    // Recarregar dados para garantir consistência
    fetchImovelData(String(response.data.id));
    if (wasCreating) {
        router.replace({ name: 'imovel-editar', params: { id: response.data.id }, query: { tab: 'imagens' } });
        activeTab.value = 'imagens';
    } else {
        alert('Salvo com sucesso!');
    }
  }
}

function handleCancel() { router.push({ name: 'imoveis' }); }

watch(imovelId, (newId) => { if(newId) fetchImovelData(newId); }, { immediate: true });
watch(() => route.query.tab, (newTab) => { if (newTab) activeTab.value = newTab as string; });
</script>

<style scoped>
/* =========================================================
   1. GERAL & HEADER
   ========================================================= */
.page-container {
  min-height: 100vh;
  background-color: #fcfcfc;
  font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
  padding: 1.5rem 2.5rem;
  display: flex; flex-direction: column;
}

.page-header { margin-bottom: 2rem; }
.title-area h1 { font-size: 1.5rem; font-weight: 300; color: #1f2937; margin: 0; letter-spacing: -0.02em; }
.breadcrumb { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.breadcrumb a { color: #94a3b8; text-decoration: none; transition: color 0.2s; }
.breadcrumb a:hover { color: #2563eb; }
.breadcrumb .separator { font-size: 0.5rem; color: #cbd5e1; }
.breadcrumb .active { color: #2563eb; font-weight: 700; }

.main-content-grid { 
    display: grid; grid-template-columns: 1fr 300px; gap: 1.5rem; align-items: start; 
}
@media (max-width: 1200px) { .main-content-grid { grid-template-columns: 1fr; } }

/* =========================================================
   2. CARD PRINCIPAL & ABAS
   ========================================================= */
.card {
  background-color: #fff; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.03); 
  border: 1px solid #e5e7eb; overflow: hidden;
}
.form-card { min-height: 500px; display: flex; flex-direction: column; }
.no-padding-body { padding: 0; }

.tabs-header {
    display: flex; flex-wrap: wrap; background-color: #f8fafc; border-bottom: 1px solid #e2e8f0;
}
.tabs-header button {
    flex: 1; min-width: 100px; padding: 1rem 0.5rem; border: none; background: transparent;
    font-size: 0.85rem; font-weight: 500; color: #64748b; cursor: pointer; transition: all 0.2s;
    border-bottom: 2px solid transparent; display: flex; align-items: center; justify-content: center; gap: 0.5rem;
}
.tabs-header button:hover { color: #334155; background-color: #f1f5f9; }
.tabs-header button.active { color: #2563eb; border-bottom-color: #2563eb; background-color: #fff; font-weight: 600; }
.tabs-header button:disabled { opacity: 0.5; cursor: not-allowed; }

.tab-content-area { padding: 2rem; flex: 1; }
.fade-in { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

/* =========================================================
   3. SEÇÕES E GRIDS
   ========================================================= */
.compact-section { margin-bottom: 0; }
.section-divider {
    font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;
    margin: 1.5rem 0 1rem 0; padding-bottom: 0.5rem; border-bottom: 1px dashed #e2e8f0;
}
.section-divider:first-child { margin-top: 0; }

.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
.checkbox-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 0.8rem; }
.checkbox-grid.dense { grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); }

.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.full-width { grid-column: 1 / -1; }

label { font-weight: 500; font-size: 0.85rem; color: #4b5563; }
.required { color: #ef4444; }

/* =========================================================
   4. INPUTS E CONTROLES
   ========================================================= */
.input-wrapper { position: relative; }
.input-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; font-size: 0.85rem; pointer-events: none; }
.form-input, .form-select, .form-textarea {
    width: 100%; padding: 0.6rem 0.75rem; border: 1px solid #d1d5db; border-radius: 6px;
    font-size: 0.9rem; transition: all 0.2s; background-color: #fff; box-sizing: border-box; color: #1f2937;
    font-family: inherit;
}
.form-input.has-icon { padding-left: 2.2rem; }
.form-input:focus, .form-select:focus, .form-textarea:focus { 
    border-color: #3b82f6; outline: none; box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}
.form-textarea { resize: vertical; min-height: 80px; }

/* Checkboxes Customizados */
.custom-checkbox {
    display: flex; align-items: center; gap: 0.6rem; cursor: pointer; font-size: 0.85rem; color: #4b5563;
    padding: 0.4rem; border-radius: 4px; transition: background 0.2s;
}
.custom-checkbox:hover { background-color: #f8fafc; }
.custom-checkbox input { accent-color: #2563eb; width: 16px; height: 16px; cursor: pointer; }

/* =========================================================
   5. COMPONENTES ESPECÍFICOS (BUSCA, BADGES)
   ========================================================= */
.search-input-wrapper { position: relative; }
.search-icon { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #94a3b8; }
.dropdown-results {
    position: absolute; top: 100%; left: 0; right: 0; background: white; border: 1px solid #cbd5e1;
    border-radius: 6px; margin-top: 4px; list-style: none; padding: 0; max-height: 200px; overflow-y: auto;
    z-index: 10; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.dropdown-results li { padding: 0.6rem 1rem; cursor: pointer; border-bottom: 1px solid #f1f5f9; transition: background 0.1s; }
.dropdown-results li:hover { background-color: #f8fafc; }
.result-name { font-weight: 500; color: #1e293b; font-size: 0.9rem; }
.result-sub { font-size: 0.75rem; color: #64748b; }

.selected-badge {
    margin-top: 0.5rem; display: flex; justify-content: space-between; align-items: center;
    background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af;
    padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.85rem;
}
.badge-content { display: flex; align-items: center; gap: 0.5rem; font-weight: 500; }
.btn-close-badge { background: none; border: none; color: #60a5fa; cursor: pointer; font-size: 0.9rem; }
.btn-close-badge:hover { color: #1e40af; }

/* Label com Ação (IA) */
.label-with-action { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem; }
.btn-text-action {
    background: none; border: none; color: #2563eb; cursor: pointer; font-size: 0.75rem; font-weight: 600;
    display: flex; align-items: center; gap: 4px; transition: color 0.2s;
}
.btn-text-action:hover { color: #1d4ed8; text-decoration: underline; }

/* Empty States */
.empty-tab-state { text-align: center; padding: 3rem; color: #94a3b8; }
.empty-tab-state i { font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.5; }
.empty-tab-state h3 { color: #475569; margin: 0 0 0.5rem 0; font-size: 1.1rem; }

/* Alert Box */
.alert-box {
    background-color: #fffbeb; border: 1px solid #fcd34d; color: #92400e; padding: 0.8rem; border-radius: 6px;
    display: flex; gap: 0.8rem; align-items: flex-start; margin-bottom: 1.5rem; font-size: 0.85rem;
}

/* Visibility Sections */
.visibility-section { margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #f1f5f9; }
.visibility-section:last-child { border-bottom: none; margin-bottom: 0; }
.visibility-title { font-size: 0.9rem; font-weight: 600; color: #334155; margin: 0 0 0.8rem 0; }

/* =========================================================
   6. COLUNA DIREITA & FOOTER
   ========================================================= */
.info-card { padding: 1.2rem; margin-bottom: 1rem; border-left: 3px solid #2563eb; }
.widget-header { margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #f1f5f9; }
.widget-title { font-size: 0.9rem; font-weight: 600; margin: 0; color: #374151; }

.status-toggle-wrapper { display: flex; align-items: center; gap: 1rem; margin-top: 0.5rem; }
.status-label { font-size: 0.9rem; font-weight: 600; }
.text-success { color: #16a34a; }
.text-muted { color: #9ca3af; }
.helper-text-widget { font-size: 0.75rem; color: #9ca3af; margin-top: 0.8rem; font-style: italic; line-height: 1.4; }

/* Switch Slider */
.switch-container { position: relative; display: inline-block; width: 44px; height: 24px; }
.switch-container input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #cbd5e1; transition: .4s; }
.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .4s; }
input:checked + .slider { background-color: #2563eb; }
input:checked + .slider:before { transform: translateX(20px); }
.slider.round { border-radius: 24px; }
.slider.round:before { border-radius: 50%; }

/* Footer Actions */
.form-footer {
    display: flex; justify-content: space-between; align-items: center;
    padding: 1.5rem 2rem; border-top: 1px solid #e2e8f0; background-color: #f8fafc;
}
.right-actions { display: flex; gap: 0.8rem; }

.btn-primary, .btn-secondary, .btn-outline-primary {
    padding: 0.6rem 1.2rem; border-radius: 6px; border: none; font-weight: 500; cursor: pointer; font-size: 0.9rem;
    display: flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
}
.btn-primary { background-color: #2563eb; color: white; box-shadow: 0 1px 2px rgba(37, 99, 235, 0.1); }
.btn-primary:hover { background-color: #1d4ed8; transform: translateY(-1px); }
.btn-secondary { background-color: white; color: #64748b; border: 1px solid #cbd5e1; }
.btn-secondary:hover { background-color: #f1f5f9; color: #334155; }
.btn-outline-primary { background-color: white; color: #2563eb; border: 1px solid #2563eb; }
.btn-outline-primary:hover { background-color: #eff6ff; }
.full-btn { width: 100%; justify-content: center; }

/* Loading */
.loading-state { text-align: center; padding: 4rem; color: #64748b; }
.spinner { border: 3px solid #e2e8f0; border-top: 3px solid #2563eb; border-radius: 50%; width: 32px; height: 32px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

@media (max-width: 1024px) {
  .page-container { padding: 1rem; }
  .tabs-header { overflow-x: auto; flex-wrap: nowrap; justify-content: flex-start; }
  .form-footer { flex-direction: column-reverse; gap: 1rem; }
  .right-actions { width: 100%; display: flex; flex-direction: column; }
  .btn-primary, .btn-outline-primary, .btn-secondary { width: 100%; justify-content: center; }
}
</style>
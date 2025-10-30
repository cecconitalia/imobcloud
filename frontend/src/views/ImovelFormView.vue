<template>
  <div class="form-container">
    <div v-if="isLoadingData" class="loading-message">
      A carregar dados do imóvel...
    </div>

    <form v-else @submit.prevent="handleSaveAndExit" class="imovel-form">
      <div class="tabs">
        <button type="button" @click="activeTab = 'geral'" :class="{ active: activeTab === 'geral' }">Geral</button>
        <button type="button" @click="activeTab = 'valores'" :class="{ active: activeTab === 'valores' }">Valores e Medidas</button>
        <button type="button" @click="activeTab = 'caracteristicas'" :class="{ active: activeTab === 'caracteristicas' }">Características</button>
        <button type="button" @click="activeTab = 'condominio'" :class="{ active: activeTab === 'condominio' }">Condomínio</button>
        <button type="button" @click="activeTab = 'imagens'" :class="{ active: activeTab === 'imagens' }" :disabled="!isEditing">Imagens</button>
        <button type="button" @click="activeTab = 'autorizacao'" :class="{ active: activeTab === 'autorizacao' }">Autorização</button>
        <button type="button" @click="activeTab = 'publico'" :class="{ active: activeTab === 'publico' }">Visibilidade Pública</button>
      </div>

      <div class="tab-content">
        <div v-show="activeTab === 'geral'">
            <div class="form-section">
                <div class="section-title">Informações Principais</div>
                <div class="form-grid">
                    <div class="form-group full-width">
                        <label for="titulo_anuncio">Título do Anúncio</label>
                        <input type="text" id="titulo_anuncio" v-model="imovel.titulo_anuncio" required />
                    </div>
                    <div class="form-group">
                        <label for="tipo">Tipo de Imóvel</label>
                        <select id="tipo" v-model="imovel.tipo" required>
                            <option value="CASA">Casa</option>
                            <option value="APARTAMENTO">Apartamento</option>
                            <option value="TERRENO">Terreno</option>
                            <option value="SALA_COMERCIAL">Sala Comercial</option>
                            <option value="GALPAO">Galpão</option>
                            <option value="RURAL">Rural</option>
                            <option value="OUTRO">Outro</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="finalidade">Finalidade</label>
                        <select id="finalidade" v-model="imovel.finalidade" required>
                            <option value="RESIDENCIAL">Residencial</option>
                            <option value="COMERCIAL">Comercial</option>
                            <option value="INDUSTRIAL">Industrial</option>
                            <option value="RURAL">Rural</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="status">Status</label>
                        <select id="status" v-model="imovel.status" required>
                            <option value="A_VENDA">À Venda</option>
                            <option value="PARA_ALUGAR">Para Alugar</option>
                            <option value="VENDIDO">Vendido</option>
                            <option value="ALUGADO">Alugado</option>
                            <option value="EM_CONSTRUCAO">Em Construção</option>
                            <option value="DESATIVADO">Desativado</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="situacao">Situação do Imóvel</label>
                        <select id="situacao" v-model="imovel.situacao">
                            <option :value="null">Não informado</option>
                            <option value="NOVO">Novo</option>
                            <option value="USADO">Usado</option>
                            <option value="NA_PLANTA">Na Planta</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="form-section">
                <div class="section-title">Endereço</div>
                <div class="form-grid">
                    <div class="form-group">
                        <label for="logradouro">Logradouro</label>
                        <input type="text" id="logradouro" v-model="imovel.logradouro" required />
                    </div>
                    <div class="form-group">
                        <label for="numero">Número</label>
                        <input type="text" id="numero" v-model="imovel.numero" />
                    </div>
                    <div class="form-group">
                        <label for="complemento">Complemento</label>
                        <input type="text" id="complemento" v-model="imovel.complemento" />
                    </div>
                    <div class="form-group">
                        <label for="bairro">Bairro</label>
                        <input type="text" id="bairro" v-model="imovel.bairro" required />
                    </div>
                    <div class="form-group">
                        <label for="cidade">Cidade</label>
                        <input type="text" id="cidade" v-model="imovel.cidade" required />
                    </div>
                    <div class="form-group">
                        <label for="estado">Estado (UF)</label>
                        <input type="text" id="estado" maxlength="2" v-model="imovel.estado" required />
                    </div>
                    <div class="form-group">
                        <label for="cep">CEP</label>
                        <input type="text" id="cep" v-model="imovel.cep" />
                    </div>
                </div>
            </div>
        </div>

        <div v-show="activeTab === 'valores'">
            <div class="form-section">
                <div class="section-title">Valores Financeiros</div>
                <div class="form-grid">
                    <div class="form-group">
                        <label for="valor_venda">Valor de Venda (R$)</label>
                        <Money3Component id="valor_venda" v-model="imovel.valor_venda" :options="moneyConfig" />
                    </div>
                    <div class="form-group">
                        <label for="valor_aluguel">Valor de Aluguel (R$)</label>
                        <Money3Component id="valor_aluguel" v-model="imovel.valor_aluguel" :options="moneyConfig" />
                    </div>
                    <div class="form-group">
                        <label for="valor_condominio">Valor do Condomínio (R$)</label>
                        <Money3Component id="valor_condominio" v-model="imovel.valor_condominio" :options="moneyConfig" />
                    </div>
                    <div class="form-group">
                        <label for="valor_iptu">Valor do IPTU (Anual, R$)</label>
                        <Money3Component id="valor_iptu" v-model="imovel.valor_iptu" :options="moneyConfig" />
                    </div>
                    </div>
            </div>
        <div class="form-section">
                <div class="section-title">Dimensões e Divisões</div>
                <div class="form-grid">
                    <div class="form-group">
                        <label for="area_total">Área Total (m²)</label>
                        <input type="number" step="0.01" id="area_total" v-model.number="imovel.area_total" />
                    </div>
                    <div class="form-group">
                        <label for="area_util">Área Útil (m²)</label>
                        <input type="number" step="0.01" id="area_util" v-model.number="imovel.area_util" />
                    </div>
                    <div class="form-group">
                        <label for="quartos">Quartos</label>
                        <input type="number" id="quartos" v-model.number="imovel.quartos" />
                    </div>
                    <div class="form-group">
                        <label for="suites">Suítes</label>
                        <input type="number" id="suites" v-model.number="imovel.suites" />
                    </div>
                    <div class="form-group">
                        <label for="banheiros">Banheiros</label>
                        <input type="number" id="banheiros" v-model.number="imovel.banheiros" />
                    </div>
                    <div class="form-group">
                        <label for="vagas_garagem">Vagas de Garagem</label>
                        <input type="number" id="vagas_garagem" v-model.number="imovel.vagas_garagem" />
                    </div>
                </div>
            </div>
        </div>

        <div v-show="activeTab === 'caracteristicas'">
            <div class="form-section">
                <div class="section-title">Características Adicionais</div>
                <div class="form-grid checkbox-grid">
                    <div class="checkbox-group">
                        <input type="checkbox" id="lavabo" v-model="imovel.lavabo">
                        <label for="lavabo">Lavabo</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="escritorio" v-model="imovel.escritorio">
                        <label for="escritorio">Escritório</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="varanda" v-model="imovel.varanda">
                        <label for="varanda">Varanda / Sacada</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="mobiliado" v-model="imovel.mobiliado">
                        <label for="mobiliado">Mobiliado</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="ar_condicionado" v-model="imovel.ar_condicionado">
                        <label for="ar_condicionado">Ar Condicionado</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="moveis_planejados" v-model="imovel.moveis_planejados">
                        <label for="moveis_planejados">Móveis Planejados</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="piscina_privativa" v-model="imovel.piscina_privativa">
                        <label for="piscina_privativa">Piscina Privativa</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="churrasqueira_privativa" v-model="imovel.churrasqueira_privativa">
                        <label for="churrasqueira_privativa">Churrasqueira Privativa</label>
                    </div>
                </div>
                
                <div class="form-group full-width" style="margin-top: 1.5rem;">
                    <div class="form-group-header">
                        <label for="descricao_completa">Descrição Detalhada (para o site)</label>
                        <button type="button" @click.prevent="handleGerarDescricaoIA" 
                                :disabled="isGerandoDescricao || !isEditing" 
                                class="btn-ai-generate"
                                title="Gerar descrição com Inteligência Artificial (necessário salvar o imóvel primeiro)">
                            <i :class="isGerandoDescricao ? 'fas fa-spinner fa-spin' : 'fas fa-magic'"></i>
                            {{ isGerandoDescricao ? 'A gerar...' : 'Gerar com IA' }}
                        </button>
                    </div>
                    <textarea id="descricao_completa" v-model="imovel.descricao_completa" rows="8"></textarea>
                </div>

                <div class="form-group full-width">
                    <label for="outras_caracteristicas">Outras Características (Opcional)</label>
                    <textarea id="outras_caracteristicas" v-model="imovel.outras_caracteristicas" rows="4"></textarea>
                </div>
            </div>
        </div>
        
        <div v-show="activeTab === 'condominio'">
             <div class="form-section">
                <div class="section-title">Infraestrutura do Condomínio</div>
                <div class="form-grid checkbox-grid">
                    <div class="checkbox-group">
                        <input type="checkbox" id="portaria_24h" v-model="imovel.portaria_24h">
                        <label for="portaria_24h">Portaria 24h</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="elevador" v-model="imovel.elevador">
                        <label for="elevador">Elevador</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="piscina_condominio" v-model="imovel.piscina_condominio">
                        <label for="piscina_condominio">Piscina no Condomínio</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="academia" v-model="imovel.academia">
                        <label for="academia">Academia</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="salao_festas" v-model="imovel.salao_festas">
                        <label for="salao_festas">Salão de Festas</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="playground" v-model="imovel.playground">
                        <label for="playground">Playground</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="quadra_esportiva" v-model="imovel.quadra_esportiva">
                        <label for="quadra_esportiva">Quadra Esportiva</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="espaco_pet" v-model="imovel.espaco_pet">
                        <label for="espaco_pet">Espaço Pet</label>
                    </div>
                </div>
            </div>
        </div>

        <div v-show="activeTab === 'imagens'">
            <div v-if="isEditing && imovel.id" class="card">
                <div class="card-header">Gestor de Imagens</div>
                <div class="card-body">
                    <ImovelImagensView :imovel-id="Number(imovel.id)" />
                </div>
            </div>
            <div v-else class="info-message">
                <p>Para adicionar imagens, primeiro guarde o imóvel.</p>
                <p>Preencha as informações nas outras abas e clique em "Salvar e Continuar".</p>
            </div>
        </div>

        <div v-show="activeTab === 'autorizacao'">
            <div class="form-section">
                <div class="section-title">Documentação e Venda</div>
                <div class="form-grid">
                    
                    <div class="form-group full-width">
                        <label for="proprietario_search">Proprietário (Buscar Cliente)</label>
                        <div class="proprietario-search-container">
                            <input 
                                type="text" 
                                id="proprietario_search" 
                                v-model="searchQuery" 
                                @input="debouncedSearch($event.target.value)"
                                placeholder="Digite nome, e-mail ou documento..."
                                :disabled="isLoadingData || isSearchingProprietario"
                                autocomplete="off"
                            />
                            
                            <p v-if="proprietarioNomeSelecionado" class="selected-proprietario-tag">
                                <i class="fas fa-user-check"></i> {{ proprietarioNomeSelecionado }} 
                                <span @click="clearProprietarioSelection" class="clear-selection-btn">&times;</span>
                            </p>
                            <p v-else-if="!searchQuery" class="info-message-small">Nenhum proprietário selecionado. Comece a digitar para buscar.</p>

                            <ul v-if="searchQuery && proprietarioSearchResults.length" class="search-results-list">
                                <li v-for="cliente in proprietarioSearchResults" 
                                    :key="cliente.id"
                                    @click="selectProprietario(cliente)">
                                    {{ cliente.nome || cliente.razao_social }} ({{ cliente.tipo_pessoa }})
                                </li>
                            </ul>
                            <div v-else-if="searchQuery && !proprietarioSearchResults.length && !isSearchingProprietario" class="search-empty-message">
                                Nenhum cliente encontrado com perfil "Proprietário".
                            </div>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="numero_matricula">Número da Matrícula</label>
                        <input type="text" id="numero_matricula" v-model="imovel.numero_matricula" />
                    </div>
                    <div class="form-group">
                        <label for="data_captacao">Data de Captação</label>
                        <input type="date" id="data_captacao" v-model="imovel.data_captacao" />
                    </div>
                    <div class="form-group">
                        <label for="data_fim_autorizacao">Data de Fim da Autorização</label>
                        <input type="date" id="data_fim_autorizacao" v-model="imovel.data_fim_autorizacao" />
                    </div>
                    <div class="form-group">
                        <label for="comissao_percentual">Comissão (%)</label>
                        <Money3Component id="comissao_percentual" v-model="imovel.comissao_percentual" :options="percentConfig" />
                    </div>
                    </div>
            </div>
            <div class="form-section">
                <div class="section-title">Status da Documentação</div>
                <div class="form-grid checkbox-grid">
                    <div class="checkbox-group">
                        <input type="checkbox" id="possui_exclusividade" v-model="imovel.possui_exclusividade">
                        <label for="possui_exclusividade">Possui Contrato de Exclusividade?</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="financiavel" v-model="imovel.financiavel">
                        <label for="financiavel">Aceita Financiamento</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="quitado" v-model="imovel.quitado">
                        <label for="quitado">Imóvel Quitado</label>
                    </div>
                    <div class="checkbox-group">
                        <input type="checkbox" id="documentacao_ok" v-model="imovel.documentacao_ok">
                        <label for="documentacao_ok">Documentação OK</label>
                    </div>
                </div>
            </div>
            <div class="form-section">
                 <div class="section-title">Observações e Ações</div>
                 <div class="form-group full-width">
                        <label for="informacoes_adicionais_autorizacao">Informações Adicionais (para o contrato)</label>
                        <textarea id="informacoes_adicionais_autorizacao" v-model="imovel.informacoes_adicionais_autorizacao" rows="4"></textarea>
                 </div>
                 <div class="form-group full-width" v-if="isEditing && imovel.id">
                        <button type="button" @click="gerarContratoPDF" class="btn-info">
                             Gerar Contrato de Autorização (PDF)
                        </button>
                 </div>
            </div>
        </div>

        <div v-show="activeTab === 'publico'" class="form-section">
            <div class="info-message">
                <p>Controle a visibilidade de cada campo deste imóvel no site público da imobiliária.</p>
                <p>Campos não selecionados não serão exibidos, mesmo que preenchidos.</p>
            </div>
             <div class="section-group">
                <div class="section-title">Opções de Ativação</div>
                <div class="checkbox-group">
                    <input type="checkbox" id="publicado_no_site" v-model="imovel.publicado_no_site">
                    <label for="publicado_no_site">Ativar Anúncio no Site Público</label>
                </div>
            </div>
            <div class="section-group" v-for="(campos, categoria) in camposVisiveis" :key="categoria">
                <div class="section-title">{{ categoria }}</div>
                <div class="form-grid checkbox-grid">
                    <div class="checkbox-group" v-for="(label, key) in campos" :key="key">
                        <input type="checkbox" :id="key" v-model="imovel.configuracao_publica[key]">
                        <label :for="key">{{ label }}</label>
                    </div>
                </div>
            </div>
        </div>
      </div>
      
      <div class="form-actions full-width">
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="button" @click="handleSaveAndContinue" class="btn-info-outline" :disabled="isSubmitting">
          {{ isSubmitting ? 'A guardar...' : 'Salvar e Continuar' }}
        </button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'A guardar...' : 'Salvar e Sair' }}
        </button>
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

// --- CORREÇÃO PROFISSIONAL: USAR O COMPONENTE EM VEZ DA DIRETIVA ---
// Isto resolve a tela branca (removendo a importação com erro) e 
// resolve o problema da máscara (usando o componente de forma explícita).
import { Money3Component } from 'v-money3';
// --- FIM DA CORREÇÃO ---


// --- CONFIGURAÇÕES V-MONEY ---
// Configuração da máscara de moeda R$
const moneyConfig = {
  debug: false,
  masked: false, // <-- Importante: 'false' armazena o número puro (1234.50) no v-model.
  prefix: 'R$ ',
  suffix: '',
  thousands: '.',
  decimal: ',',
  precision: 2,
  disableNegative: true,
  disabled: false,
  min: 0.0,
  max: 999999999999.99,
  allowBlank: true,
  minimumNumberOfCharacters: 0,
};

// Configuração para percentual (usado na comissão)
const percentConfig = {
  debug: false,
  masked: false,
  prefix: '',
  suffix: ' %',
  thousands: '.',
  decimal: ',',
  precision: 2,
  disableNegative: true,
  disabled: false,
  min: 0.0,
  max: 100.0,
  allowBlank: true,
  minimumNumberOfCharacters: 0,
};
// --- FIM DAS CONFIGURAÇÕES ---


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
    'Informações Gerais': {
        'titulo_anuncio': 'Título do Anúncio',
        'tipo': 'Tipo de Imóvel',
        'finalidade': 'Finalidade',
        'status': 'Status',
    },
    'Valores': {
        'valor_venda': 'Valor de Venda',
        'valor_aluguel': 'Valor de Aluguel',
        'valor_condominio': 'Valor do Condomínio',
        'valor_iptu': 'Valor do IPTU',
    },
    'Localização': {
        'logradouro': 'Logradouro',
        'numero': 'Número',
        'complemento': 'Complemento',
        'bairro': 'Bairro',
        'cidade': 'Cidade',
        'estado': 'Estado',
        'cep': 'CEP',
    },
    'Dimensões': {
        'area_construida': 'Área Construída',
        'area_util': 'Área Útil',
        'area_total': 'Área Total',
        'quartos': 'Quartos',
        'suites': 'Suítes',
        'banheiros': 'Banheiros',
        'vagas_garagem': 'Vagas de Garagem',
    },
    'Detalhes e Comodidades': {
        'descricao_completa': 'Descrição Detalhada',
        'outras_caracteristicas': 'Outras Características',
        'lavabo': 'Lavabo',
        'escritorio': 'Escritório',
        'varanda': 'Varanda',
        'mobiliado': 'Mobiliado',
        'ar_condicionado': 'Ar Condicionado',
        'moveis_planejados': 'Móveis Planejados',
        'piscina_privativa': 'Piscina Privativa',
        'churrasqueira_privativa': 'Churrasqueira Privativa',
        'portaria_24h': 'Portaria 24h',
        'elevador': 'Elevador',
        'piscina_condominio': 'Piscina no Condomínio',
        'academia': 'Academia',
        'salao_festas': 'Salão de Festas',
        'playground': 'Playground',
        'quadra_esportiva': 'Quadra Esportiva',
        'espaco_pet': 'Espaço Pet',
        'financiavel': 'Aceita Financiamento',
        'quitado': 'Imóvel Quitado',
        'documentacao_ok': 'Documentação OK',
        'aceita_pet': 'Aceita Pet',
    },
};

const createEmptyImovel = () => {
    const allPublicKeys = Object.values(camposVisiveis).flatMap(obj => Object.keys(obj));
    const defaultConfig = allPublicKeys.reduce((acc, key) => {
        acc[key] = true;
        return acc;
    }, {} as { [key: string]: boolean });

    return {
        id: null,
        titulo_anuncio: '',
        codigo_referencia: '',
        tipo: 'CASA',
        finalidade: 'RESIDENCIAL',
        status: 'A_VENDA',
        situacao: null,
        publicado_no_site: true,
        valor_venda: null,
        valor_aluguel: null,
        valor_condominio: null,
        valor_iptu: null,
        logradouro: '',
        numero: '',
        complemento: '',
        bairro: '',
        cidade: '',
        estado: '',
        cep: '',
        quartos: 0,
        suites: 0,
        banheiros: 0,
        vagas_garagem: 0,
        lavabo: false,
        escritorio: false,
        varanda: false,
        mobiliado: false,
        ar_condicionado: false,
        moveis_planejados: false,
        piscina_privativa: false,
        churrasqueira_privativa: false,
        portaria_24h: false,
        elevador: false,
        piscina_condominio: false,
        academia: false,
        salao_festas: false,
        playground: false,
        quadra_esportiva: false,
        espaco_pet: false,
        financiavel: false,
        quitado: false,
        documentacao_ok: false,
        aceita_pet: false,
        proprietario: null,
        numero_matricula: '',
        data_captacao: null,
        data_fim_autorizacao: null,
        possui_exclusividade: false,
        comissao_percentual: null,
        informacoes_adicionais_autorizacao: '',
        posicao_chave: '',
        outras_caracteristicas: '',
        descricao_completa: '', 
        configuracao_publica: defaultConfig,
        proprietario_detalhes: null as any 
    };
};

const imovel = ref(createEmptyImovel());

async function fetchImovelData(id: string) {
  if (!id) return; 

  isLoadingData.value = true;
  try {
    const { data } = await apiClient.get(`/v1/imoveis/${id}/`);
    const emptyImovel = createEmptyImovel();
    imovel.value = { 
      ...emptyImovel,
      ...data,
      proprietario: data.proprietario_detalhes?.id || null,
      proprietario_detalhes: data.proprietario_detalhes || null, 
      configuracao_publica: { ...emptyImovel.configuracao_publica, ...data.configuracao_publica }
    };
  } catch (error) {
    console.error('Erro ao carregar dados do imóvel:', error);
    alert('Não foi possível carregar os dados do imóvel.');
  } finally {
    isLoadingData.value = false;
  }
}

const searchProprietarios = async (query: string) => {
    if (!query || query.length < 3) {
        proprietarioSearchResults.value = [];
        return;
    }

    isSearchingProprietario.value = true;
    try {
        const response = await apiClient.get('/v1/clientes/', { 
            params: { 
                tipo: 'PROPRIETARIO',
                search: query,
                status: 'ativo'
            } 
        });
        proprietarioSearchResults.value = response.data;
    } catch (error) {
        console.error("Erro ao buscar clientes:", error);
        proprietarioSearchResults.value = [];
    } finally {
        isSearchingProprietario.value = false;
    }
};

const debouncedSearch = debounce(searchProprietarios, 300); 

function selectProprietario(cliente: any) {
    imovel.value.proprietario = cliente.id; 
    imovel.value.proprietario_detalhes = cliente; 
    proprietarioSearchResults.value = []; 
    searchQuery.value = ''; 
}

function clearProprietarioSelection() {
    imovel.value.proprietario = null;
    imovel.value.proprietario_detalhes = null;
}

async function gerarContratoPDF() {
    if (!imovel.value.id) return;
    if (!imovel.value.proprietario) {
         alert("Para gerar o contrato, selecione um 'Proprietário'.");
         activeTab.value = 'autorizacao'; // Muda para a aba de autorização
         return;
    }
    
    // CORREÇÃO: Usar POST para enviar dados customizados do formulário
    try {
        const payload = {
            comissao_percentual: imovel.value.comissao_percentual,
            data_fim_autorizacao: imovel.value.data_fim_autorizacao,
            informacoes_adicionais: imovel.value.informacoes_adicionais_autorizacao,
        };
        
        const response = await apiClient.post(`/v1/imoveis/${imovel.value.id}/gerar-autorizacao-pdf/`, payload, { 
            responseType: 'blob' 
        });
        
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        
        const contentDisposition = response.headers['content-disposition'];
        let fileName = `autorizacao_imovel_${imovel.value.codigo_referencia}.pdf`;
        if (contentDisposition) {
            const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
            if (fileNameMatch && fileNameMatch.length === 2) fileName = fileNameMatch[1];
        }
        
        link.setAttribute('download', fileName);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
        
    } catch (error: any) {
        console.error("Erro ao gerar PDF:", error);
        
        if (error.response && error.response.data && error.response.data.type === 'application/json') {
             const reader = new FileReader();
             reader.onload = () => {
                 try {
                     const errorJson = JSON.parse(reader.result as string);
                     alert(`Erro ao gerar PDF: ${errorJson.error || 'Erro desconhecido.'}`);
                 } catch (e) {
                      alert(`Erro ao gerar PDF: ${reader.result}`);
                 }
             };
             reader.readAsText(error.response.data);
        } else if (error.response && error.response.data) {
             const errorMessage = await error.response.data.text();
             alert(`Erro ao gerar PDF: ${errorMessage}`);
        } else {
             alert('Erro desconhecido ao gerar o PDF.');
        }
    }
}

async function handleGerarDescricaoIA() {
    if (!isEditing.value || !imovel.value.id) {
        alert("Por favor, salve o imóvel antes de gerar uma descrição com IA.");
        return;
    }

    isGerandoDescricao.value = true;
    try {
        const response = await apiClient.post(`/v1/imoveis/${imovel.value.id}/gerar-descricao-ia/`);
        
        if (response.data && response.data.descricao) {
            imovel.value.descricao_completa = response.data.descricao;
            alert("Descrição gerada com sucesso!");
        } else {
            throw new Error("A resposta da API não continha uma descrição.");
        }

    } catch (error: any) {
        console.error("Erro ao gerar descrição com IA:", error);
        const errorMsg = error.response?.data?.error || "Não foi possível gerar a descrição. Verifique o console.";
        alert(`Erro: ${errorMsg}`);
    } finally {
        isGerandoDescricao.value = false;
    }
}

watch(imovelId, () => {
  fetchImovelData(imovelId.value || '');
}, { immediate: true }); 

watch(() => route.query.tab, (newTab) => {
  if (newTab) activeTab.value = newTab as string;
});

onMounted(() => {
  // onMounted
});

// --- CORREÇÃO DE SINTAXE ---
// A função saveImovel estava truncada na resposta anterior. 
// Esta é a versão completa e correta.
async function saveImovel() {
  isSubmitting.value = true;
  const payload = { ...imovel.value };
  
  delete payload.id;
  delete payload.proprietario_detalhes; 

  Object.keys(payload).forEach(key => {
    // Não remover o 'proprietario' se for null (para desassociar)
    if (key !== 'proprietario' && payload[key] === null) {
        delete payload[key];
    }
  });
  
  try {
    if (isEditing.value) {
      return await apiClient.put(`/v1/imoveis/${imovelId.value}/`, payload);
    } else {
      return await apiClient.post('/v1/imoveis/', payload);
    }
  } catch (error: any) {
    console.error("Erro ao guardar o imóvel:", error.response?.data || error);
    
    // Tenta extrair mensagens de erro da API do Django REST Framework
    if (error.response && error.response.data) {
        let errorMessages = [];
        const data = error.response.data;
        if (typeof data === 'object') {
            for (const key in data) {
                if (Array.isArray(data[key])) {
                    errorMessages.push(`${key}: ${data[key].join(', ')}`);
                } else {
                    errorMessages.push(`${key}: ${data[key]}`);
                }
            }
        }
        if (errorMessages.length > 0) {
            alert(`Ocorreu um erro ao guardar:\n${errorMessages.join('\n')}`);
        } else {
             alert('Ocorreu um erro desconhecido ao guardar o imóvel.');
        }
    } else {
        alert('Ocorreu um erro ao guardar o imóvel.');
    }
    return null;
  } finally {
    isSubmitting.value = false;
  }
}
// --- FIM DA CORREÇÃO DE SINTAXE ---

async function handleSaveAndExit() {
  const response = await saveImovel();
  if (response && response.data) {
    // Não precisamos atualizar o imovel.value aqui, pois estamos a sair
    alert('Imóvel guardado com sucesso!');
    router.push({ name: 'imoveis' });
  }
}

async function handleSaveAndContinue() {
  const response = await saveImovel();
  if (response && response.data) {
    const wasCreating = !isEditing.value;
    
    const emptyImovel = createEmptyImovel();
    imovel.value = {
        ...emptyImovel,
        ...response.data,
        proprietario: response.data.proprietario_detalhes?.id || null, // Garante que o ID está no proprietario
        proprietario_detalhes: response.data.proprietario_detalhes || null,
        configuracao_publica: { ...emptyImovel.configuracao_publica, ...response.data.configuracao_publica }
    };
    
    alert('Imóvel guardado com sucesso!');

    if (wasCreating && response.data.id) {
        // Atualiza a URL para o modo de edição
        await router.push({ name: 'imovel-editar', params: { id: response.data.id }, query: { tab: 'geral' } });
    }
    
    // Sugere a próxima aba mais lógica após guardar
    if (wasCreating) {
      activeTab.value = 'imagens';
    }
  }
}

function handleCancel() {
  router.push({ name: 'imoveis' });
}
</script>

<style scoped>
.form-container { 
  padding: 0; 
}

.tabs { display: flex; flex-wrap: wrap; border-bottom: 2px solid #ccc; margin-bottom: 1.5rem; width: 100%; }
.tabs button { padding: 10px 20px; border: none; background: none; cursor: pointer; font-size: 1rem; font-weight: 500; color: #6c757d; border-bottom: 2px solid transparent; margin-bottom: -2px; }
.tabs button:disabled { color: #ccc; cursor: not-allowed; }
.tabs button.active { color: #007bff; border-bottom-color: #007bff; font-weight: bold; }
.tab-content { width: 100%; }
.imovel-form { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; width: 100%; }
.form-group { display: flex; flex-direction: column; }
.form-group.full-width { grid-column: 1 / -1; }
label { margin-bottom: 0.5rem; font-weight: 500; }

/* Estilo base para inputs, selects e textareas */
input, select, textarea { 
  padding: 10px; 
  border: 1px solid #ccc; 
  border-radius: 4px; 
  font-size: 1rem; 
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  width: 100%; /* Garante que todos ocupem o espaço do form-group */
  box-sizing: border-box; /* Garante que o padding não quebre o layout */
}

/* CORREÇÃO DE ESTILO: 
   O <Money3Component> renderiza um <input> dentro de uma <span>.
   Usamos :deep() para forçar o estilo no input interno do componente, 
   fazendo com que ele se pareça exatamente com os outros inputs.
*/
:deep(.v-money3 input) {
  padding: 10px; 
  border: 1px solid #ccc; 
  border-radius: 4px; 
  font-size: 1rem; 
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  width: 100%;
  box-sizing: border-box;
  text-align: right; /* Aplica o alinhamento à direita */
}

/* Remove a borda da <span> externa do componente v-money3 */
:deep(.v-money3 span) {
  border: none !important;
  display: block; /* Faz a span ocupar a largura total */
}

/* Remove o estilo antigo que não funciona mais */
/* input[v-money] {
  text-align: right;
} */


.checkbox-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
.checkbox-group { display: flex; align-items: center; gap: 0.5rem; }
.checkbox-group input[type="checkbox"] { width: auto; }
.checkbox-group label { margin-bottom: 0; font-weight: normal; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; width: 100%; margin-top: 1rem; }
.btn-primary, .btn-secondary, .btn-info, .btn-info-outline { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; font-weight: 500; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif; }
.btn-primary { background-color: #007bff; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-info { background-color: #17a2b8; color: white; }
.btn-info-outline { background-color: white; color: #17a2b8; border: 1px solid #17a2b8; }
.loading-message { text-align: center; padding: 2rem; }
.info-message { background-color: #e9f5ff; border: 1px solid #b3d7f7; color: #0d6efd; padding: 1rem; border-radius: 4px; text-align: center; width: 100%; }
.card { background-color: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; width: 100%; }
.mt-4 { margin-top: 1.5rem; }
.mt-3 { margin-top: 1rem; }
.card-header { background-color: #f7f7f7; padding: 1rem 1.5rem; font-weight: bold; border-bottom: 1px solid #e0e0e0; }
.card-body { padding: 1.5rem; }
.form-label { font-weight: bold; }
.form-control { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
.spinner-border { display: inline-block; width: 1rem; height: 1rem; vertical-align: text-bottom; border: .2em solid currentColor; border-right-color: transparent; border-radius: 50%; -webkit-animation: spinner-border .75s linear infinite; animation: spinner-border .75s linear infinite; }
@-webkit-keyframes spinner-border { to { -webkit-transform: rotate(360deg); } }
@keyframes spinner-border { to { transform: rotate(360deg); } }
.spinner-border-sm { width: 0.8rem; height: 0.8rem; border-width: .15em; }

.plataformas-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.section-group {
    border: 1px solid #e9ecef;
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 1.5rem;
    background-color: #f8f9fa;
}
.section-title {
    font-size: 1.1rem;
    font-weight: bold;
    color: #343a40;
    margin-top: 0;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e0e0e0;
}

.form-section {
    background-color: #f9fafb;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
}

.proprietario-search-container {
    position: relative;
    display: flex;
    flex-direction: column;
}

.proprietario-search-container input[type="text"] {
    position: relative;
    z-index: 11; 
}

.search-results-list {
    position: absolute;
    top: 100%; 
    left: 0;
    right: 0;
    z-index: 10;
    background: white;
    border: 1px solid #007bff;
    border-top: none;
    max-height: 200px;
    overflow-y: auto;
    list-style: none;
    padding: 0;
    margin-top: 0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    border-radius: 0 0 4px 4px;
}

.search-results-list li {
    padding: 10px;
    cursor: pointer;
    border-bottom: 1px solid #f0f0f0;
    font-size: 0.95rem;
}

.search-results-list li:hover {
    background-color: #e6f7ff;
    color: #007bff;
}

.selected-proprietario-tag {
    background-color: #d4edda;
    color: #155724;
    padding: 8px 12px;
    border-radius: 4px;
    font-weight: 500;
    margin-top: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1rem;
}
.selected-proprietario-tag i {
    margin-right: 8px;
}

.clear-selection-btn {
    cursor: pointer;
    font-size: 1.2rem;
    font-weight: bold;
    padding: 0 5px;
    margin-left: 10px;
}

.search-empty-message {
    padding: 10px;
    text-align: center;
    color: #888;
    background-color: #fff;
    border: 1px solid #ccc;
    border-top: none;
    border-radius: 0 0 4px 4px;
    position: absolute;
    width: 100%;
    top: 100%;
    z-index: 9;
    font-size: 0.9rem;
}

.info-message-small {
    font-size: 0.8rem;
    color: #6c757d;
    margin-top: 5px;
}

.form-group-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem; 
}
.form-group-header label {
    margin-bottom: 0; 
}
.btn-ai-generate {
    padding: 5px 10px;
    font-size: 0.8rem;
    background-color: #e6f7ff;
    color: #0056b3;
    border: 1px solid #0056b3;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 5px;
    font-weight: 500;
}
.btn-ai-generate:disabled {
    background-color: #eee;
    color: #999;
    border-color: #ccc;
    cursor: not-allowed;
}
.btn-ai-generate .fa-magic {
    color: #0056b3;
}
</style>
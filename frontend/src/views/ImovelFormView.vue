<template>
  <div class="form-container">
    <header class="view-header">
      <h1>{{ isEditing ? `Editar Imóvel #${imovel.codigo_referencia}` : 'Adicionar Novo Imóvel' }}</h1>
      <div class="header-actions">
        <router-link to="/imoveis" class="btn-secondary">Voltar à Lista</router-link>
      </div>
    </header>

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
                        <input type="number" step="0.01" id="valor_venda" v-model.number="imovel.valor_venda" />
                    </div>
                    <div class="form-group">
                        <label for="valor_aluguel">Valor de Aluguel (R$)</label>
                        <input type="number" step="0.01" id="valor_aluguel" v-model.number="imovel.valor_aluguel" />
                    </div>
                    <div class="form-group">
                        <label for="valor_condominio">Valor do Condomínio (R$)</label>
                        <input type="number" step="0.01" id="valor_condominio" v-model.number="imovel.valor_condominio" />
                    </div>
                    <div class="form-group">
                        <label for="valor_iptu">Valor do IPTU (Anual, R$)</label>
                        <input type="number" step="0.01" id="valor_iptu" v-model.number="imovel.valor_iptu" />
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
                    <div class="form-group">
                        <label for="proprietario">Proprietário (Cliente)</label>
                        <select id="proprietario" v-model="imovel.proprietario">
                            <option :value="null">-- Selecione um Cliente --</option>
                            <option v-for="cliente in clientes" :key="cliente.id" :value="cliente.id">
                                {{ cliente.nome_completo }}
                            </option>
                        </select>
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
                        <input type="number" step="0.01" id="comissao_percentual" v-model.number="imovel.comissao_percentual" />
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

const route = useRoute();
const router = useRouter();

const imovelId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!imovelId.value);
const activeTab = ref('geral');
const clientes = ref<any[]>([]);

// Campos que podem ter a visibilidade controlada no site público, separados por categoria
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
        configuracao_publica: defaultConfig,
    };
};

const imovel = ref(createEmptyImovel());
const isLoadingData = ref(false);
const isSubmitting = ref(false);

async function fetchClientes() {
    try {
        const response = await apiClient.get('/v1/clientes/');
        clientes.value = response.data;
    } catch (error) {
        console.error("Erro ao carregar clientes:", error);
    }
}

async function fetchImovelData() {
  if (isEditing.value && imovelId.value) {
    isLoadingData.value = true;
    try {
      const { data } = await apiClient.get(`/v1/imoveis/${imovelId.value}/`);
      const emptyImovel = createEmptyImovel();
      // Mescla os dados para garantir que todos os campos reativos existam
      imovel.value = { 
        ...emptyImovel,
        ...data,
        // Garante que o ID do proprietário seja usado para o v-model
        proprietario: data.proprietario_detalhes?.id || null,
        configuracao_publica: { ...emptyImovel.configuracao_publica, ...data.configuracao_publica }
      };
    } catch (error) {
      console.error('Erro ao carregar dados do imóvel:', error);
      alert('Não foi possível carregar os dados do imóvel.');
    } finally {
      isLoadingData.value = false;
    }
  } else {
    imovel.value = createEmptyImovel();
  }
}

async function gerarContratoPDF() {
    if (!imovel.value.id) return;
    if (!imovel.value.proprietario || !imovel.value.data_captacao || !imovel.value.data_fim_autorizacao) {
        alert("Para gerar o contrato, preencha os campos: Proprietário, Data de Captação e Data de Fim da Autorização.");
        return;
    }
    try {
        const response = await apiClient.get(`/v1/imoveis/${imovel.value.id}/gerar-autorizacao-pdf/`, { responseType: 'blob' });
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
    }
}

watch(imovelId, () => {
  fetchImovelData();
}, { immediate: true }); 

watch(() => route.query.tab, (newTab) => {
  if (newTab) activeTab.value = newTab as string;
});

onMounted(() => {
  fetchClientes();
});

async function saveImovel() {
  isSubmitting.value = true;
  const payload = { ...imovel.value };
  
  delete payload.id;
  Object.keys(payload).forEach(key => {
    // Mantém o 'proprietario' como null se for o caso, não remove
    if (key !== 'proprietario' && payload[key] === null) delete payload[key];
  });
  
  try {
    if (isEditing.value) {
      return await apiClient.put(`/v1/imoveis/${imovelId.value}/`, payload);
    } else {
      return await apiClient.post('/v1/imoveis/', payload);
    }
  } catch (error: any) {
    console.error("Erro ao guardar o imóvel:", error.response?.data || error);
    alert('Ocorreu um erro ao guardar o imóvel.');
    return null;
  } finally {
    isSubmitting.value = false;
  }
}

async function handleSaveAndExit() {
  const response = await saveImovel();
  if (response && response.data) {
    // Atualiza o estado local com a resposta antes de sair
    imovel.value = { ...imovel.value, ...response.data };
    alert('Imóvel guardado com sucesso!');
    router.push({ name: 'imoveis' });
  }
}

async function handleSaveAndContinue() {
  const response = await saveImovel();
  if (response && response.data) {
    const wasCreating = !isEditing.value;
    
    // ATUALIZAÇÃO CRÍTICA: Mescla a resposta da API com o estado local
    const emptyImovel = createEmptyImovel();
    imovel.value = {
        ...emptyImovel,
        ...response.data,
        configuracao_publica: { ...emptyImovel.configuracao_publica, ...response.data.configuracao_publica }
    };
    
    alert('Imóvel guardado com sucesso!');

    if (wasCreating && response.data.id) {
        // Se estava a criar, navega para a nova rota de edição
        await router.push({ name: 'imovel-editar', params: { id: response.data.id } });
    }
    
    // Muda para a aba de imagens após salvar
    activeTab.value = 'imagens';
  }
}

function handleCancel() {
  router.push({ name: 'imoveis' });
}
</script>

<style scoped>
/* Estilos existentes */
.form-container { padding: 2rem; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.tabs { display: flex; flex-wrap: wrap; border-bottom: 2px solid #ccc; margin-bottom: 1.5rem; width: 100%; }
.tabs button { padding: 10px 20px; border: none; background: none; cursor: pointer; font-size: 1rem; font-weight: 500; color: #6c757d; border-bottom: 2px solid transparent; margin-bottom: -2px; }
.tabs button:disabled { color: #ccc; cursor: not-allowed; }
.tabs button.active { color: #007bff; border-bottom-color: #007bff; font-weight: bold; }
.tab-content { width: 100%; }
.imovel-form { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; width: 100%; }
.form-group { display: flex; flex-direction: column; }
.form-group.full-width { grid-column: 1 / -1; }
label { margin-bottom: 0.5rem; font-weight: bold; }
input, select, textarea { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
.checkbox-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
.checkbox-group { display: flex; align-items: center; gap: 0.5rem; }
.checkbox-group input[type="checkbox"] { width: auto; }
.checkbox-group label { margin-bottom: 0; font-weight: normal; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; width: 100%; margin-top: 1rem; }
.btn-primary, .btn-secondary, .btn-info, .btn-info-outline { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; font-weight: bold; }
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

.header-actions {
  display: flex;
  gap: 1rem;
}

/* NOVOS ESTILOS PARA O LAYOUT DA ABA DE VISIBILIDADE */
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

/* NOVO ESTILO PARA AS SEÇÕES DO FORMULÁRIO */
.form-section {
    background-color: #f9fafb;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
}
</style>
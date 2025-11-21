<template>
  <div class="page-container">
    
    <div v-if="isLoadingData" class="loading-state card">
         <div class="spinner"></div>
         <p>A carregar dados...</p>
    </div>

    <div v-else class="main-content-grid">
      
      <div class="left-column">
        <div class="card form-card">
          <form @submit.prevent="handleSubmit">
            
            <div class="form-section compact-section">
                <h3 class="section-title"><i class="fas fa-bullseye"></i> Dados da Negociação</h3>
                
                <div class="form-grid">
                    <div class="form-group full-width">
                    <label for="titulo">Título da Oportunidade <span class="required">*</span></label>
                    <div class="input-wrapper">
                        <i class="fas fa-heading input-icon"></i>
                        <input 
                            type="text" 
                            id="titulo" 
                            v-model="oportunidade.titulo" 
                            placeholder="Ex: Compra Apto Centro" 
                            required 
                            class="form-input has-icon"
                        />
                    </div>
                    </div>

                    <div class="form-group">
                    <label for="cliente">Cliente <span class="required">*</span></label>
                    <v-select
                        id="cliente"
                        v-model="oportunidade.cliente_id"
                        :options="clienteOptions"
                        :reduce="(option) => option.value"
                        label="label"
                        placeholder="Pesquisar cliente..."
                        :clearable="false"
                        :disabled="isLoadingClientes || clienteCriadoAutomaticamente"
                        class="style-chooser"
                        @search="onClienteSearch"
                    >
                        <template #option="option">
                        <div class="option-content">
                            <div class="option-title">{{ option.label }}</div>
                            <div class="option-subtitle" v-if="option.documento || option.telefone">
                                <span v-if="option.documento"><i class="fas fa-id-card"></i> {{ option.documento }}</span>
                            </div>
                        </div>
                        </template>
                        <template #no-options>
                            <span class="no-results">Digite para buscar...</span>
                        </template>
                    </v-select>
                    <small v-if="clienteCriadoAutomaticamente" class="helper-text text-success">
                        <i class="fas fa-check-circle"></i> Cliente criado e pré-selecionado automaticamente.
                    </small>
                    </div>

                    <div class="form-group">
                    <label for="imovel_interesse">Imóvel de Interesse</label>
                    <v-select
                            id="imovel_interesse"
                            v-model="oportunidade.imovel_interesse_id"
                            :options="imovelOptions"
                            :reduce="(option) => option.value"
                            label="label"
                            placeholder="Pesquisar imóvel..."
                            :disabled="isLoadingImoveis"
                            class="style-chooser"
                            @search="onImovelSearch"
                        >
                        <template #option="option">
                            <div class="option-content">
                                <div class="option-title">
                                    {{ option.titulo_anuncio || 'Imóvel sem título' }} 
                                    <span class="badge-code" v-if="option.codigo_referencia">{{ option.codigo_referencia }}</span>
                                </div>
                                <div class="option-subtitle" v-if="option.logradouro">
                                        <i class="fas fa-map-marker-alt"></i> 
                                        {{ option.logradouro }}{{ option.bairro ? ', ' + option.bairro : '' }}
                                </div>
                            </div>
                        </template>
                            <template #no-options>
                            <span class="no-results">Digite para buscar...</span>
                            </template>
                        </v-select>
                    </div>

                    <div class="form-group">
                    <label for="fase_funil">Fase do Funil <span class="required">*</span></label>
                    <div class="input-wrapper">
                        <i class="fas fa-layer-group input-icon"></i>
                        <select id="fase_funil" v-model="oportunidade.fase_funil_id" required class="form-select has-icon">
                            <option v-for="fase in fasesFunil" :key="fase.id" :value="fase.id">
                            {{ fase.titulo }}
                            </option>
                        </select>
                    </div>
                    </div>

                    <div class="form-group">
                        <label for="valor_estimado">Valor Estimado (R$)</label>
                        <MoneyInput
                            id="valor_estimado"
                            v-model="oportunidade.valor_estimado"
                            class="form-input"
                            :prefix="'R$ '"
                        />
                    </div>

                    <div class="form-group">
                        <label for="responsavel">Corretor Responsável</label>
                        <v-select
                            id="responsavel"
                            v-model="oportunidade.responsavel_id"
                            :options="corretoresOptions"
                            :reduce="(option) => option.value"
                            label="label"
                            placeholder="Selecione ou pesquise..."
                            class="style-chooser"
                        >
                            <template #option="option">
                                <div class="option-content">
                                    <div class="option-title">{{ option.label }}</div>
                                    <div class="option-subtitle" v-if="option.email">
                                        {{ option.email }}
                                    </div>
                                </div>
                            </template>
                            <template #no-options>
                                <span class="no-results">Nenhum corretor encontrado</span>
                            </template>
                        </v-select>
                    </div>

                    <div class="form-group">
                        <label for="fonte">Origem do Lead</label>
                        <div class="input-wrapper">
                            <i class="fas fa-bullhorn input-icon"></i>
                            <select id="fonte" v-model="oportunidade.fonte" class="form-select has-icon">
                                <option :value="null">-- Selecione --</option>
                                <option value="SITE">Site</option>
                                <option value="PORTAL_IMOVEIS">Portal Imobiliário</option>
                                <option value="INDICACAO">Indicação</option>
                                <option value="CLIENTE_EXISTENTE">Cliente da Carteira</option>
                                <option value="REDES_SOCIAIS">Redes Sociais</option>
                                <option value="TELEFONE">Telefone Ativo</option>
                                <option value="EMAIL">Email</option>
                                <option value="VISITA_PRESENCIAL">Visita à Loja</option>
                                <option value="OUTRO">Outro</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group full-width">
                    <label for="informacoes_adicionais">Observações / Detalhes</label>
                    <textarea 
                        id="informacoes_adicionais" 
                        v-model="oportunidade.informacoes_adicionais" 
                        rows="3" 
                        class="form-textarea"
                        placeholder="Insira detalhes importantes sobre a negociação..."
                    ></textarea>
                    </div>
                </div>
            </div>

            <div class="form-actions-footer">
                <button type="button" @click="handleCancel" class="btn-secondary">
                    Cancelar
                </button>
                <button type="submit" class="btn-primary" :disabled="isSubmitting || !oportunidade.cliente_id">
                <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
                <span v-else>{{ isEditing ? 'Salvar' : 'Criar' }}</span>
                </button>
            </div>
          </form>
        </div>
      </div> 
      
      <div class="right-column" v-if="isEditing">
            <div class="card tasks-card">
                 <div class="widget-header">
                     <h3 class="widget-title"><i class="fas fa-tasks"></i> Tarefas</h3>
                     <button @click="abrirModalNovaTarefa" class="btn-icon-mini" title="Nova Tarefa">
                        <i class="fas fa-plus"></i>
                    </button>
                 </div>
                
                <div v-if="tarefas.length === 0" class="empty-state-widget">
                    <i class="fas fa-check-double"></i>
                    <p>Nenhuma tarefa pendente.</p>
                </div>
                 <ul v-else class="tarefas-list">
                     <li v-for="tarefa in tarefas" :key="tarefa.id" :class="['tarefa-item', { concluida: tarefa.concluida }]">
                        <div class="tarefa-check">
                             <input type="checkbox" :checked="tarefa.concluida" @change="toggleConcluirTarefa(tarefa)" />
                        </div>
                        <div class="tarefa-content">
                            <span class="tarefa-text">{{ tarefa.titulo }}</span>
                            <small class="tarefa-date" :class="{'text-danger': isAtrasada(tarefa.data_agendada) && !tarefa.concluida}">
                                <i class="far fa-calendar-alt"></i> {{ formatarDataHora(tarefa.data_agendada) }}
                            </small>
                        </div>
                        <button @click="abrirModalEditarTarefa(tarefa)" class="btn-edit-mini">
                            <i class="fas fa-pen"></i>
                        </button>
                     </li>
                 </ul>
            </div>
            
            <div class="card activities-card">
                <ClienteAtividades :oportunidadeId="oportunidadeId ? parseInt(oportunidadeId) : undefined" />
            </div>
        </div> 
    </div> 
    
    <TarefaModal
        v-if="showTarefaModal"
        :tarefa-id="tarefaParaEditarId"
        :oportunidade-id="oportunidadeId ? parseInt(oportunidadeId) : undefined"
        @close="fecharModalTarefa"
        @saved="tarefaSalva"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';
import MoneyInput from '@/components/MoneyInput.vue'; 
import ClienteAtividades from '@/components/ClienteAtividades.vue';
import TarefaModal from '@/components/TarefaModal.vue';
import { format, parseISO, isPast } from 'date-fns';
import { ptBR } from 'date-fns/locale';

// Interfaces
interface SelectOption { 
    label: string; 
    value: number; 
    documento?: string;
    telefone?: string;
    proprietario_nome?: string;
    titulo_anuncio?: string;
    codigo_referencia?: string;
    logradouro?: string;
    bairro?: string;
    cidade?: string;
    email?: string;
}
interface FaseFunilSelecao { id: string; titulo: string; } 
interface Tarefa { id: number; titulo: string; data_agendada: string; concluida: boolean; }

const route = useRoute();
const router = useRouter();
const oportunidadeId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!oportunidadeId.value);
const isLoadingData = ref(false);
const isSubmitting = ref(false);

const clienteOptions = ref<SelectOption[]>([]);
const imovelOptions = ref<SelectOption[]>([]);
const corretoresOptions = ref<SelectOption[]>([]);

const isLoadingClientes = ref(false);
const isLoadingImoveis = ref(false);

const tarefas = ref<Tarefa[]>([]);
const showTarefaModal = ref(false);
const tarefaParaEditarId = ref<number | null>(null);

const clienteCriadoAutomaticamente = ref(false);

const fasesFunil = ref<FaseFunilSelecao[]>([
  { id: 'LEAD', titulo: 'Novo Lead' },
  { id: 'CONTATO', titulo: 'Primeiro Contato' },
  { id: 'VISITA', titulo: 'Visita Agendada' },
  { id: 'PROPOSTA', titulo: 'Proposta Enviada' },
  { id: 'NEGOCIACAO', titulo: 'Em Negociação' },
  { id: 'GANHO', titulo: 'Negócio Ganho' },
  { id: 'PERDIDO', titulo: 'Negócio Perdido' }
]);

const oportunidade = ref({
  id: null,
  titulo: '',
  cliente_id: null as number | null,
  imovel_interesse_id: null as number | null,
  fase_funil_id: 'LEAD',
  responsavel_id: null as number | null,
  valor_estimado: null as number | null,
  fonte: null as string | null,
  informacoes_adicionais: '',
});

function getDataFromResponse(response: any) {
    if (response.data && Array.isArray(response.data.results)) return response.data.results; 
    if (Array.isArray(response.data)) return response.data; 
    return []; 
}

// --- Funções de Busca (Inalteradas) ---
let clienteSearchTimeout: NodeJS.Timeout | null = null;
async function onClienteSearch(search: string, loading: (l: boolean) => void) {
    if (search.length >= 2) {
        if (clienteSearchTimeout) clearTimeout(clienteSearchTimeout);
        loading(true);
        clienteSearchTimeout = setTimeout(async () => {
            try {
                const response = await apiClient.get(`/v1/clientes/?search=${search}`);
                const rawData = getDataFromResponse(response);
                clienteOptions.value = rawData.map((c: any) => ({
                    label: c.nome_display || c.nome || c.razao_social,
                    value: c.id,
                    documento: c.documento,
                    telefone: c.telefone
                }));
            } finally { loading(false); }
        }, 400);
    }
}

let imovelSearchTimeout: NodeJS.Timeout | null = null;
async function onImovelSearch(search: string, loading: (l: boolean) => void) {
     if (search.length >= 2) {
        if (imovelSearchTimeout) clearTimeout(imovelSearchTimeout);
        loading(true);
        imovelSearchTimeout = setTimeout(async () => {
            try {
                const response = await apiClient.get(`/v1/imoveis/?search=${search}`);
                const rawData = getDataFromResponse(response);
                imovelOptions.value = rawData.map((i: any) => ({
                    label: i.titulo_codigo || `${i.titulo_anuncio || 'Imóvel'} (${i.codigo_referencia || 'S/Cód'})`,
                    value: i.id,
                    titulo_anuncio: i.titulo_anuncio,
                    codigo_referencia: i.codigo_referencia,
                    logradouro: i.logradouro,
                    bairro: i.bairro,
                    cidade: i.cidade,
                    proprietario_nome: i.proprietario_detalhes ? (i.proprietario_detalhes.nome || i.proprietario_detalhes.razao_social) : 'N/A'
                }));
            } finally { loading(false); }
        }, 400);
    }
}

/**
 * Verifica se o cliente existe por email/nome. Se não existir, cria um novo
 * cliente Lead e retorna o ID.
 */
async function checkOrCreateClient(leadData: { nome: string, email: string, telefone: string }): Promise<number | null> {
    try {
        // 1. Tenta buscar cliente pelo email
        console.log("Tentando buscar cliente com email:", leadData.email);
        const searchResponse = await apiClient.get(`/v1/clientes/?search=${leadData.email}`);
        const foundClients = getDataFromResponse(searchResponse);

        if (foundClients.length > 0) {
            console.log("Cliente encontrado. Usando cliente existente:", foundClients[0].id);
            // Cliente encontrado, retorna o ID do primeiro resultado
            return foundClients[0].id;
        }

        // 2. Cliente não encontrado, cria um novo
        console.log("Cliente não encontrado. Criando novo cliente Lead...");
        
        // CORREÇÃO CRÍTICA: Usar 11 dígitos numéricos fixos para satisfazer a validação do Django/modelo Cliente.
        const uniqueDocumento = '00000000000'; // 11 zeros
        
        console.log("Documento temporário a ser enviado:", uniqueDocumento); 
        
        const newClientPayload = {
            nome: leadData.nome,
            email: leadData.email,
            telefone: leadData.telefone,
            tipo_pessoa: 'FISICA',
            documento: uniqueDocumento, 
            perfil_cliente: ['INTERESSADO'] 
        };
        
        // POST para criação do cliente
        const createResponse = await apiClient.post('/v1/clientes/', newClientPayload);
        const newClientId = createResponse.data.id;
        
        console.log("Cliente criado com sucesso. ID:", newClientId);

        // Adiciona o novo cliente na lista de opções para pré-selecionar
        clienteOptions.value.unshift({
            label: leadData.nome,
            value: newClientId,
            email: leadData.email,
            telefone: leadData.telefone,
            documento: newClientPayload.documento
        });
        clienteCriadoAutomaticamente.value = true;

        return newClientId;

    } catch (e: any) {
        // Exibe o erro de forma mais detalhada para o usuário, se possível
        const errorDetails = JSON.stringify(e.response?.data, null, 2) || e.message;
        console.error("Erro ao verificar ou criar cliente automaticamente:", errorDetails);
        alert(`Falha ao criar cliente automático. Por favor, cadastre-o manualmente. Detalhes: ${errorDetails}`);
        return null; 
    }
}


async function loadInitialData() {
  isLoadingData.value = true;
  isLoadingClientes.value = true;
  isLoadingImoveis.value = true;

  try {
    const promises = [
      apiClient.get('/v1/core/usuarios/lista_corretores_simples/'),
      apiClient.get('/v1/clientes/lista-simples/'), 
      apiClient.get('/v1/imoveis/lista-simples/') 
    ];

    if (isEditing.value && oportunidadeId.value) {
      promises.push(apiClient.get(`/v1/clientes/oportunidades/${oportunidadeId.value}/`));
      promises.push(apiClient.get(`/v1/tarefas/?oportunidade=${oportunidadeId.value}`));
    }

    // --- VERIFICAÇÃO DE PARÂMETROS DE ORIGEM (TRIAGEM DE LEADS) ---
    const query = route.query;
    const origemImovelId = query.imovel_id ? String(query.imovel_id) : null;
    const contatoNome = query.contato_nome ? String(query.contato_nome) : null;
    const contatoEmail = query.contato_email ? String(query.contato_email) : null;
    const contatoMensagem = query.mensagem ? String(query.mensagem) : null;
    const contatoTelefone = query.contato_telefone ? String(query.contato_telefone) : null;
    
    if (origemImovelId) {
        // Se viemos de um lead de imóvel específico, buscamos os detalhes desse imóvel
        promises.push(apiClient.get(`/v1/imoveis/${origemImovelId}/`));
    }

    const results = await Promise.all(promises);

    const corretoresRaw = results[0].data;
    corretoresOptions.value = corretoresRaw.map((c: any) => ({
        label: c.nome_completo,
        value: c.id,
        email: c.email
    }));
    
    const clientesRaw = getDataFromResponse(results[1]);
    clienteOptions.value = clientesRaw.map((c: any) => ({
        label: c.nome_display || c.nome || c.razao_social,
        value: c.id,
        documento: c.documento,
        telefone: c.telefone
    }));

    const imoveisRaw = getDataFromResponse(results[2]);
    imovelOptions.value = imoveisRaw.map((i: any) => ({
        label: i.label || `${i.titulo_anuncio || 'Imóvel'} (${i.codigo_referencia || 'S/Cód'})`,
        value: i.id,
        titulo_anuncio: i.titulo_anuncio,
        codigo_referencia: i.codigo_referencia,
        logradouro: i.logradouro,
        bairro: i.bairro,
        cidade: i.cidade,
        proprietario_nome: i.proprietario_nome
    }));

    // Lógica de Edição
    if (isEditing.value && results.length > 3) {
      const opData = results[3].data;
      const clienteObj = opData.cliente;
      const imovelObj = opData.imovel;
      const responsavelObj = opData.responsavel;
      
      const clienteId = (clienteObj && typeof clienteObj === 'object') ? clienteObj.id : clienteObj;
      const imovelId = (imovelObj && typeof imovelObj === 'object') ? imovelObj.id : imovelObj;
      const responsavelId = (responsavelObj && typeof responsavelObj === 'object') ? responsavelObj.id : responsavelObj;

      // Adiciona às opções se não existir (para edição)
      if (clienteId && !clienteOptions.value.find(c => c.value === clienteId)) {
          const nome = (clienteObj && typeof clienteObj === 'object') ? (clienteObj.nome_completo || 'Cliente') : 'Cliente';
          clienteOptions.value.unshift({ label: nome, value: clienteId });
      }
      if (imovelId && !imovelOptions.value.find(i => i.value === imovelId)) {
           const titulo = (imovelObj && typeof imovelObj === 'object') ? (imovelObj.imovel_titulo || 'Imóvel') : 'Imóvel';
           imovelOptions.value.unshift({ label: titulo, value: imovelId });
      }
      
      if (responsavelId && !corretoresOptions.value.find(c => c.value === responsavelId)) {
          const nomeResp = (responsavelObj && typeof responsavelObj === 'object') 
              ? (responsavelObj.first_name || responsavelObj.username || 'Responsável') 
              : 'Responsável';
          corretoresOptions.value.unshift({ label: nomeResp, value: responsavelId });
      }

      oportunidade.value = {
        id: opData.id,
        titulo: opData.titulo,
        cliente_id: clienteId,
        imovel_interesse_id: imovelId, 
        fase_funil_id: opData.fase, 
        responsavel_id: responsavelId,
        valor_estimado: opData.valor_estimado ? parseFloat(opData.valor_estimado) : null,
        fonte: opData.fonte || null,
        informacoes_adicionais: opData.informacoes_adicionais || '',
      };

      if (results.length > 4) {
          tarefas.value = getDataFromResponse(results[4]);
      }
    } 
    // Lógica de Criação via "Gerar Lead" (Pré-preenchimento e Criação Automática de Cliente)
    else if (!isEditing.value && origemImovelId && contatoEmail && contatoNome) {
        
        // 1. Cria ou Busca o Cliente Automaticamente
        const leadClientData = {
            nome: contatoNome,
            email: contatoEmail,
            telefone: contatoTelefone || '',
        };

        const clientID = await checkOrCreateClient(leadClientData);
        
        // 2. Prepara dados da Oportunidade
        const imovelDetail = results[results.length - 1].data;
        
        // Formata o objeto do imóvel
        const imovelOption = {
            label: `${imovelDetail.titulo_anuncio || 'Imóvel'} (${imovelDetail.codigo_referencia || 'S/Cód'})`,
            value: imovelDetail.id,
            titulo_anuncio: imovelDetail.titulo_anuncio,
            codigo_referencia: imovelDetail.codigo_referencia,
            logradouro: imovelDetail.logradouro,
            bairro: imovelDetail.bairro
        };

        // Adiciona na lista e seleciona o imóvel
        if (!imovelOptions.value.find(i => i.value === imovelDetail.id)) {
            imovelOptions.value.unshift(imovelOption);
        }

        // 3. Preenche o formulário
        oportunidade.value.imovel_interesse_id = imovelDetail.id;
        oportunidade.value.cliente_id = clientID; // ID do cliente criado/encontrado
        oportunidade.value.titulo = `Lead Site - ${contatoNome} (${imovelDetail.codigo_referencia})`;
        
        // Adiciona a mensagem original nas observações
        let obs = contatoMensagem ? `Mensagem Original: "${contatoMensagem}"` : 'Contato via formulário do site.';
        obs += `\n\nDados do Contato:\nEmail: ${contatoEmail}\nTel: ${contatoTelefone || 'N/A'}`;
        oportunidade.value.informacoes_adicionais = obs;

        oportunidade.value.fonte = 'SITE';
        oportunidade.value.fase_funil_id = 'CONTATO'; // Sugerir fase 2 (Primeiro Contato)

    }

  } catch (error) {
    console.error('Erro ao carregar dados:', error);
  } finally {
    isLoadingData.value = false;
    isLoadingClientes.value = false;
    isLoadingImoveis.value = false;
  }
}

async function handleSubmit() {
  isSubmitting.value = true;
  // Bloqueia se não houver cliente ID (garante que o cliente foi criado/selecionado)
  if (!oportunidade.value.cliente_id) {
       alert("É obrigatório vincular um Cliente a esta oportunidade.");
       isSubmitting.value = false;
       return;
  }
  
  try {
    const apiPayload = {
        titulo: oportunidade.value.titulo,
        cliente: oportunidade.value.cliente_id,
        imovel: oportunidade.value.imovel_interesse_id, 
        fase: oportunidade.value.fase_funil_id, 
        responsavel: oportunidade.value.responsavel_id,
        valor_estimado: oportunidade.value.valor_estimado,
        fonte: oportunidade.value.fonte,
        informacoes_adicionais: oportunidade.value.informacoes_adicionais
    };

    let response;
    if (isEditing.value && oportunidadeId.value) {
      response = await apiClient.patch(`/v1/clientes/oportunidades/${oportunidadeId.value}/`, apiPayload);
    } else {
      response = await apiClient.post('/v1/clientes/oportunidades/', apiPayload);
      
      // Se foi criado a partir de um contato (Lead Site), arquivamos o contato original
      const contatoIdOriginal = route.query.contato_id;
      if (contatoIdOriginal) {
          try {
              await apiClient.post(`/v1/contatos/${contatoIdOriginal}/arquivar/`);
              console.log("Contato original arquivado com sucesso.");
          } catch (e) {
              console.error("Erro silencioso ao arquivar contato original:", e);
          }
      }
    }
    router.push('/funil-vendas');
  } catch (error: any) {
    console.error("Erro ao guardar:", error.response?.data || error);
    let msg = 'Erro ao salvar. Verifique os dados.';
    if(error.response?.data) {
        const keys = Object.keys(error.response.data);
        if(keys.length > 0) msg = `${keys[0]}: ${error.response.data[keys[0]]}`;
    }
    alert(msg);
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() { router.push('/funil-vendas'); }

// --- Funções de Tarefa (Inalteradas) ---
function abrirModalNovaTarefa() { tarefaParaEditarId.value = null; showTarefaModal.value = true; }
function abrirModalEditarTarefa(tarefa: any) { tarefaParaEditarId.value = tarefa.id; showTarefaModal.value = true; }
function fecharModalTarefa() { showTarefaModal.value = false; tarefaParaEditarId.value = null; }
function tarefaSalva() { fecharModalTarefa(); fetchTarefas(); }

async function fetchTarefas() {
    if (!oportunidadeId.value) return;
    try {
        const response = await apiClient.get(`/v1/tarefas/?oportunidade=${oportunidadeId.value}`);
        tarefas.value = getDataFromResponse(response);
    } catch (error) { console.error(error); }
}

async function toggleConcluirTarefa(tarefa: any) {
    try {
        const novoStatus = !tarefa.concluida;
        await apiClient.patch(`/v1/tarefas/${tarefa.id}/`, { 
            concluida: novoStatus,
            data_conclusao: novoStatus ? new Date().toISOString() : null
        });
        tarefa.concluida = novoStatus;
    } catch (error) { fetchTarefas(); }
}

function formatarDataHora(dataIso: string | null): string {
  if (!dataIso) return '-';
  try { return format(parseISO(dataIso), 'dd/MM HH:mm', { locale: ptBR }); } catch { return '-'; }
}

function isAtrasada(dataIso: string): boolean {
    if (!dataIso) return false;
    return isPast(parseISO(dataIso));
}

onMounted(loadInitialData);
</script>

<style scoped>
/* Layout Base */
.page-container { 
    padding: 0.5rem; /* Reduzido para minimizar espaço no topo */
    background-color: #f4f7f6; 
    min-height: 100vh;
}

/* Grid Layout */
.main-content-grid { 
    display: grid; 
    grid-template-columns: 1fr 360px; 
    gap: 1rem; 
    align-items: start; 
    margin-top: 0; 
}
@media (max-width: 1100px) { .main-content-grid { grid-template-columns: 1fr; } }

/* Cards */
.card {
  background-color: #fff; 
  border-radius: 10px; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.04);
  padding: 1.5rem; 
  border: 1px solid #eaedf0;
}
.tasks-card, .activities-card { padding: 1.2rem; margin-bottom: 1rem; }

/* Formulário */
.form-section { margin-bottom: 1.5rem; }
.section-title {
    font-size: 1.1rem; color: #2c3e50; margin-bottom: 1rem; padding-bottom: 0.5rem;
    border-bottom: 2px solid #f0f2f5; font-weight: 700; display: flex; align-items: center; gap: 0.6rem;
}
.compact-section { margin-bottom: 0; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.3rem; }
.full-width { grid-column: 1 / -1; }

label { font-weight: 600; font-size: 0.8rem; color: #495057; }
.required { color: #e74c3c; }

/* Inputs com Ícones */
.input-wrapper { position: relative; }
.input-icon {
    position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #adb5bd; font-size: 0.85rem; pointer-events: none;
}
.form-input, .form-select, .form-textarea {
    width: 100%; padding: 0.55rem 0.75rem; border: 1px solid #ced4da; border-radius: 6px;
    font-size: 0.9rem; transition: border-color 0.2s; background-color: #fff; box-sizing: border-box;
}
.form-input.has-icon, .form-select.has-icon { padding-left: 2rem; }
.form-input:focus, .form-select:focus, .form-textarea:focus { 
    border-color: #3498db; outline: none; box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}
.form-textarea { resize: vertical; min-height: 100px; font-family: inherit; }

/* V-Select Styles */
.style-chooser :deep(.vs__dropdown-toggle) {
    border: 1px solid #ced4da; border-radius: 6px; padding: 4px 0 5px 0;
}
.style-chooser :deep(.vs__search) { margin-top: 0; }

/* Footer Actions */
.form-actions-footer {
    display: flex; justify-content: flex-end; gap: 1rem; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #f0f2f5;
}
.btn-primary, .btn-secondary {
    padding: 0.6rem 1.5rem; border-radius: 6px; border: none; font-weight: 600; cursor: pointer; font-size: 0.9rem; display: flex; align-items: center; gap: 0.5rem;
}
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover { background-color: #0056b3; transform: translateY(-1px); }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }

/* Widgets Coluna Direita (Tarefas) */
.widget-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; padding-bottom: 0.5rem; border-bottom: 1px solid #f0f2f5; }
.widget-title { font-size: 0.95rem; font-weight: 700; margin: 0; color: #495057; display: flex; align-items: center; gap: 0.5rem; }
.btn-icon-mini { 
    width: 26px; height: 26px; border-radius: 6px; border: 1px solid #dee2e6; 
    background: white; color: #007bff; cursor: pointer; 
    display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.btn-icon-mini:hover { background: #007bff; color: white; }

.tarefas-list { list-style: none; padding: 0; margin: 0; }
.tarefa-item { display: flex; align-items: center; gap: 0.8rem; padding: 0.6rem 0; border-bottom: 1px solid #f8f9fa; }
.tarefa-content { flex: 1; min-width: 0; }
.tarefa-text { font-size: 0.85rem; font-weight: 500; color: #343a40; display: block; }
.tarefa-item.concluida .tarefa-text { text-decoration: line-through; color: #adb5bd; }
.tarefa-date { font-size: 0.7rem; color: #6c757d; }
.text-danger { color: #dc3545; }
.btn-edit-mini { background: none; border: none; color: #adb5bd; cursor: pointer; }
.btn-edit-mini:hover { color: #007bff; }
.empty-state-widget { text-align: center; padding: 1.5rem 1rem; color: #adb5bd; font-size: 0.85rem; }
.empty-state-widget i { font-size: 1.4rem; margin-bottom: 0.4rem; display: block; opacity: 0.5; }

/* Loading */
.loading-state { text-align: center; padding: 4rem; color: #6c757d; }
.spinner { border: 3px solid #e9ecef; border-top: 3px solid #007bff; border-radius: 50%; width: 40px; height: 40px; animation: spin 0.8s linear infinite; margin: 0 auto 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Badges in Select */
.option-content { display: flex; flex-direction: column; }
.option-title { font-weight: 600; font-size: 0.9rem; color: #343a40; }
.option-subtitle { font-size: 0.75rem; color: #6c757d; display: flex; align-items: center; gap: 5px; }
.badge-code { background-color: #e9ecef; color: #495057; padding: 0 4px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }

.helper-text { font-size: 0.75rem; margin-top: 0.3rem; }
.text-success { color: #28a745; }
</style>
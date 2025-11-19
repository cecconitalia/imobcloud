<template>
  <div class="page-container">
    
    <div class="main-content-grid">
      <div class="left-column">
        
        <div v-if="isLoadingData" class="loading-state card">
             <div class="spinner"></div>
             <p>A carregar dados...</p>
        </div>

        <form v-else @submit.prevent="handleSubmit" class="oportunidade-form card">
          
          <div class="form-grid">
            <div class="form-group full-width">
              <label for="titulo">Título da Oportunidade <span class="required">*</span></label>
              <input 
                type="text" 
                id="titulo" 
                v-model="oportunidade.titulo" 
                placeholder="Ex: Compra Apto Centro" 
                required 
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="cliente">Cliente <span class="required">*</span></label>
              <v-select
                id="cliente"
                v-model="oportunidade.cliente_id"
                :options="clienteOptions"
                :reduce="(option) => option.value"
                label="label"
                placeholder="Busque por nome, CPF/CNPJ ou telefone..."
                :clearable="false"
                :disabled="isLoadingClientes"
                class="style-chooser"
                @search="onClienteSearch"
              >
                 <template #option="option">
                   <div class="option-content">
                       <div class="option-title">{{ option.label }}</div>
                       <div class="option-subtitle" v-if="option.documento || option.telefone">
                          <span v-if="option.documento" class="badge-info"><i class="fas fa-id-card"></i> {{ option.documento }}</span>
                          <span v-if="option.telefone" class="badge-info"><i class="fas fa-phone-alt"></i> {{ option.telefone }}</span>
                       </div>
                   </div>
                 </template>
                 <template #no-options>
                    <span class="no-results">Digite para buscar...</span>
                 </template>
              </v-select>
              <p v-if="isLoadingClientes" class="help-text-loading">Carregando clientes...</p>
            </div>

            <div class="form-group">
              <label for="imovel_interesse">Imóvel de Interesse</label>
               <v-select
                    id="imovel_interesse"
                    v-model="oportunidade.imovel_interesse_id"
                    :options="imovelOptions"
                    :reduce="(option) => option.value"
                    label="label"
                    placeholder="Busque por cód., título, endereço ou proprietário..."
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
                           <div class="option-subtitle">
                                <span v-if="option.proprietario_nome" class="badge-owner">
                                    <i class="fas fa-user-tie"></i> {{ option.proprietario_nome }}
                                </span>
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
                <p v-if="isLoadingImoveis" class="help-text-loading">Carregando imóveis...</p>
            </div>

             <div class="form-group">
              <label for="fase_funil">Fase do Funil <span class="required">*</span></label>
              <select id="fase_funil" v-model="oportunidade.fase_funil_id" required class="form-select">
                <option v-for="fase in fasesFunil" :key="fase.id" :value="fase.id">
                  {{ fase.titulo }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="valor_estimado">Valor Estimado (R$)</label>
              <input 
                type="number" 
                step="0.01" 
                id="valor_estimado" 
                v-model.number="oportunidade.valor_estimado" 
                placeholder="0,00" 
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="responsavel">Corretor Responsável</label>
              <select id="responsavel" v-model="oportunidade.responsavel_id" class="form-select">
                <option :value="null">-- Selecione --</option>
                <option v-for="corretor in corretores" :key="corretor.id" :value="corretor.id">
                  {{ corretor.first_name }} {{ corretor.last_name || '' }}
                </option>
              </select>
            </div>

             <div class="form-group">
                <label for="fonte">Origem do Lead</label>
                <select id="fonte" v-model="oportunidade.fonte" class="form-select">
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

            <div class="form-group full-width">
              <label for="informacoes_adicionais">Observações / Detalhes</label>
              <textarea 
                id="informacoes_adicionais" 
                v-model="oportunidade.informacoes_adicionais" 
                rows="3" 
                class="form-textarea"
                placeholder="Insira detalhes importantes..."
              ></textarea>
            </div>
          </div>

          <div class="form-actions-footer">
            <button type="button" @click="handleCancel" class="btn-secondary">
                Cancelar
            </button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
              <span v-else>{{ isEditing ? 'Salvar Alterações' : 'Criar Oportunidade' }}</span>
            </button>
          </div>
        </form>
      </div> 
      
      <div class="right-column" v-if="isEditing">
            <div class="card tasks-card">
                 <div class="widget-header">
                     <h3 class="widget-title">Tarefas</h3>
                     <button @click="abrirModalNovaTarefa" class="btn-icon-mini" title="Nova Tarefa">
                        <i class="fas fa-plus"></i>
                    </button>
                 </div>
                
                <div v-if="tarefas.length === 0" class="empty-state-widget">
                    <p>Nenhuma tarefa pendente.</p>
                </div>
                 <ul v-else class="tarefas-list">
                     <li v-for="tarefa in tarefas" :key="tarefa.id" :class="['tarefa-item', { concluida: tarefa.concluida }]">
                        <div class="tarefa-check">
                             <input type="checkbox" :checked="tarefa.concluida" @change="toggleConcluirTarefa(tarefa)" />
                        </div>
                        <div class="tarefa-content">
                            <span class="tarefa-text">{{ tarefa.titulo }}</span>
                            <small class="tarefa-date">{{ formatarDataHora(tarefa.data_agendada) }}</small>
                        </div>
                        <button @click="abrirModalEditarTarefa(tarefa)" class="btn-edit-mini">
                            <i class="fas fa-pen"></i>
                        </button>
                     </li>
                 </ul>
            </div>
            <ClienteAtividades :oportunidadeId="oportunidadeId ? parseInt(oportunidadeId) : undefined" />
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
import ClienteAtividades from '@/components/ClienteAtividades.vue';
import TarefaModal from '@/components/TarefaModal.vue';
import { format, parseISO } from 'date-fns';
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
}
interface UserSelecao { id: number; first_name: string; last_name?: string; }
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
const isLoadingClientes = ref(false);
const isLoadingImoveis = ref(false);

const corretores = ref<UserSelecao[]>([]);
const tarefas = ref<Tarefa[]>([]);
const showTarefaModal = ref(false);
const tarefaParaEditarId = ref<number | null>(null);

// Fases Fixas
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
  valor_estimado: null,
  fonte: null,
  informacoes_adicionais: '',
});

function getDataFromResponse(response: any) {
    if (response.data && Array.isArray(response.data.results)) return response.data.results; 
    if (Array.isArray(response.data)) return response.data; 
    return []; 
}

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

async function loadInitialData() {
  isLoadingData.value = true;
  isLoadingClientes.value = true;
  isLoadingImoveis.value = true;

  try {
    const promises = [
      apiClient.get<UserSelecao[]>('/v1/core/usuarios/?cargo=Corretor'),
      apiClient.get('/v1/clientes/lista-simples/'), 
      apiClient.get('/v1/imoveis/lista-simples/') 
    ];

    if (isEditing.value && oportunidadeId.value) {
      promises.push(apiClient.get(`/v1/clientes/oportunidades/${oportunidadeId.value}/`));
      promises.push(apiClient.get(`/v1/clientes/tarefas/?oportunidade=${oportunidadeId.value}`));
    }

    const results = await Promise.all(promises);

    corretores.value = getDataFromResponse(results[0]);
    
    const clientesRaw = getDataFromResponse(results[1]);
    clienteOptions.value = clientesRaw.map((c: any) => ({
        label: c.nome_display || c.nome || c.razao_social,
        value: c.id,
        documento: c.documento,
        telefone: c.telefone
    }));

    const imoveisRaw = getDataFromResponse(results[2]);
    imovelOptions.value = imoveisRaw.map((i: any) => ({
        label: i.label || `${i.titulo_anuncio} (${i.codigo_referencia})`,
        value: i.value,
        titulo_anuncio: i.titulo_anuncio,
        codigo_referencia: i.codigo_referencia,
        logradouro: i.logradouro,
        bairro: i.bairro,
        cidade: i.cidade,
        proprietario_nome: i.proprietario_nome
    }));

    if (isEditing.value && results.length > 3) {
      const opData = results[3].data;

      // === CORREÇÃO CRÍTICA: Extrair ID do objeto se for objeto ===
      const clienteObj = opData.cliente;
      const imovelObj = opData.imovel;
      const responsavelObj = opData.responsavel;
      
      const clienteId = (clienteObj && typeof clienteObj === 'object') ? clienteObj.id : clienteObj;
      const imovelId = (imovelObj && typeof imovelObj === 'object') ? imovelObj.id : imovelObj;
      const responsavelId = (responsavelObj && typeof responsavelObj === 'object') ? responsavelObj.id : responsavelObj;

      // Adiciona à lista de opções se não existir (para o select funcionar)
      if (clienteId && !clienteOptions.value.find(c => c.value === clienteId)) {
          const nome = (clienteObj && typeof clienteObj === 'object') 
              ? (clienteObj.nome_completo || 'Cliente') 
              : 'Cliente';
          clienteOptions.value.unshift({ label: nome, value: clienteId });
      }
      if (imovelId && !imovelOptions.value.find(i => i.value === imovelId)) {
           const titulo = (imovelObj && typeof imovelObj === 'object') 
               ? (imovelObj.imovel_titulo || 'Imóvel') 
               : 'Imóvel';
           imovelOptions.value.unshift({ label: titulo, value: imovelId });
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

    if (isEditing.value && oportunidadeId.value) {
      await apiClient.patch(`/v1/clientes/oportunidades/${oportunidadeId.value}/`, apiPayload);
    } else {
      await apiClient.post('/v1/clientes/oportunidades/', apiPayload);
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

// --- Funções de Tarefa ---
function abrirModalNovaTarefa() { tarefaParaEditarId.value = null; showTarefaModal.value = true; }
function abrirModalEditarTarefa(tarefa: any) { tarefaParaEditarId.value = tarefa.id; showTarefaModal.value = true; }
function fecharModalTarefa() { showTarefaModal.value = false; tarefaParaEditarId.value = null; }
function tarefaSalva() { fecharModalTarefa(); fetchTarefas(); }

async function fetchTarefas() {
    if (!oportunidadeId.value) return;
    try {
        const response = await apiClient.get(`/v1/clientes/tarefas/?oportunidade=${oportunidadeId.value}`);
        tarefas.value = getDataFromResponse(response);
    } catch (error) { console.error(error); }
}

async function toggleConcluirTarefa(tarefa: any) {
    try {
        const novoStatus = !tarefa.concluida;
        await apiClient.patch(`/v1/clientes/tarefas/${tarefa.id}/`, { 
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

onMounted(loadInitialData);
</script>

<style scoped>
.page-container { 
    padding: 1.5rem; 
    background-color: #f4f7f6; 
    min-height: 100vh;
}

.main-content-grid { 
    display: grid; 
    grid-template-columns: 1fr 320px; 
    gap: 1.5rem; 
    align-items: start; 
}
@media (max-width: 992px) { .main-content-grid { grid-template-columns: 1fr; } }

/* Card Padrão */
.card {
  background-color: #fff; 
  border-radius: 8px; 
  box-shadow: 0 2px 6px rgba(0,0,0,0.04);
  padding: 1.5rem; 
  border: 1px solid #e9ecef;
}

/* Formulário */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.full-width { grid-column: 1 / -1; }

label { font-weight: 600; font-size: 0.85rem; color: #495057; }
.required { color: #dc3545; }

/* Inputs Padronizados */
.form-input, .form-select, .form-textarea {
    width: 100%; padding: 0.55rem 0.75rem;
    border: 1px solid #ced4da; border-radius: 5px;
    font-size: 0.9rem; transition: border-color 0.2s;
    background-color: #fff;
}
.form-input:focus, .form-select:focus, .form-textarea:focus { 
    border-color: #80bdff; outline: 0; 
}
.form-textarea { resize: vertical; min-height: 80px; font-family: inherit; }

/* V-Select Personalizado */
.style-chooser :deep(.vs__dropdown-toggle) {
    border: 1px solid #ced4da; border-radius: 5px; padding: 3px 0 5px 0;
    font-size: 0.9rem;
}
.style-chooser :deep(.vs__search) { margin-top: 2px; }

.option-content {
    display: flex; flex-direction: column; padding: 2px 0;
}
.option-title { font-weight: 600; color: #343a40; font-size: 0.9rem; }
.option-subtitle { 
    font-size: 0.75rem; color: #6c757d; margin-top: 2px; 
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.badge-info { display: inline-flex; align-items: center; gap: 4px; }
.badge-code {
    background-color: #e9ecef; color: #495057; padding: 1px 5px;
    border-radius: 4px; font-size: 0.7rem; font-weight: 700; margin-left: 5px;
}
.badge-owner {
    background-color: #e0f2fe; color: #0369a1; padding: 1px 6px;
    border-radius: 4px; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;
}

/* Botões */
.form-actions-footer {
    display: flex; justify-content: flex-end; gap: 0.8rem;
    margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #f0f2f5;
}
.btn-primary, .btn-secondary {
    padding: 0.5rem 1.2rem; border-radius: 5px; border: none;
    font-weight: 600; cursor: pointer; font-size: 0.9rem;
}
.btn-primary { background-color: #007bff; color: white; }
.btn-primary:hover { background-color: #0056b3; }
.btn-primary:disabled { background-color: #ccc; cursor: not-allowed; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5a6268; }

/* Tarefas */
.tasks-card { padding: 1rem; margin-bottom: 1rem; }
.widget-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #f0f2f5; }
.widget-title { font-size: 1rem; font-weight: 700; margin: 0; color: #495057; }
.btn-icon-mini { 
    width: 26px; height: 26px; border-radius: 50%; border: 1px solid #dee2e6; 
    background: white; color: #007bff; cursor: pointer; 
    display: flex; align-items: center; justify-content: center; 
}
.btn-icon-mini:hover { background: #007bff; color: white; }

.tarefas-list { list-style: none; padding: 0; margin: 0; }
.tarefa-item { display: flex; align-items: center; gap: 0.8rem; padding: 0.7rem 0; border-bottom: 1px solid #f8f9fa; }
.tarefa-content { flex: 1; min-width: 0; }
.tarefa-text { font-size: 0.9rem; font-weight: 500; color: #343a40; display: block; }
.tarefa-item.concluida .tarefa-text { text-decoration: line-through; color: #adb5bd; }
.tarefa-date { font-size: 0.75rem; color: #6c757d; }
.btn-edit-mini { background: none; border: none; color: #adb5bd; cursor: pointer; }
.btn-edit-mini:hover { color: #007bff; }
.empty-state-widget { text-align: center; padding: 1rem; color: #999; font-size: 0.85rem; }

.loading-state { text-align: center; padding: 3rem; color: #6c757d; }
.spinner { border: 3px solid #f3f3f3; border-top: 3px solid #007bff; border-radius: 50%; width: 30px; height: 30px; animation: spin 0.8s linear infinite; margin: 0 auto 10px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
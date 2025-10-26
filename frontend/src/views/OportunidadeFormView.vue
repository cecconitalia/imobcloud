<template>
  <div class="page-container">
    <div class="main-content-grid">
      <div class="left-column">
        <div v-if="isLoadingData" class="loading-message card">
          A carregar dados...
        </div>

        <form v-else @submit.prevent="handleSubmit" class="oportunidade-form card">
          <h3 class="card-title">{{ isEditing ? 'Editar Oportunidade' : 'Adicionar Nova Oportunidade' }}</h3>
          <div class="form-grid">
            <div class="form-group full-width">
              <label for="titulo">Título da Oportunidade</label>
              <input type="text" id="titulo" v-model="oportunidade.titulo" placeholder="Ex: Venda do apartamento X para o cliente Y" required />
            </div>
            <div class="form-group">
              <label for="cliente">Cliente</label>
              <v-select
                id="cliente"
                label="nome_identificacao" :options="clientes"
                :reduce="(cliente: any) => cliente.id"
                v-model="oportunidade.cliente_id"
                placeholder="Digite para buscar um cliente"
                required
                :filterable="true"
                @search="onClienteSearch"
              >
                 <template #option="option">
                   {{ option.nome_identificacao }} </template>
                 <template #selected-option="option">
                    {{ option.nome_identificacao }} </template>
                <template #no-options>
                  Nenhum cliente encontrado. <router-link to="/clientes/novo" target="_blank">Criar Novo?</router-link>
                </template>
              </v-select>
            </div>
             <div class="form-group">
              <label for="imovel_interesse">Imóvel de Interesse (Opcional)</label>
               <v-select
                    id="imovel_interesse"
                    label="titulo_codigo" :options="imoveis"
                    :reduce="(imovel: any) => imovel.id"
                    v-model="oportunidade.imovel_interesse_id"
                    placeholder="Digite Cód. Ref ou Título"
                    :filterable="true"
                    @search="onImovelSearch"
                >
                   <template #option="option">
                       {{ option.titulo_codigo }} </template>
                   <template #selected-option="option">
                       {{ option.titulo_codigo }} </template>
                    <template #no-options>
                      Nenhum imóvel encontrado.
                    </template>
                </v-select>
            </div>
             <div class="form-group">
              <label for="fase_funil">Fase do Funil</label>
              <select id="fase_funil" v-model="oportunidade.fase_funil_id" required>
                <option v-for="fase in fasesFunil" :key="fase.id" :value="fase.id">
                  {{ fase.nome }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="responsavel">Responsável (Corretor)</label>
              <select id="responsavel" v-model="oportunidade.responsavel_id">
                <option :value="null">-- Nenhum --</option>
                <option v-for="corretor in corretores" :key="corretor.id" :value="corretor.id">
                  {{ corretor.first_name }} {{ corretor.last_name || '' }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label for="valor_estimado">Valor Estimado (R$)</label>
              <input type="number" step="0.01" id="valor_estimado" v-model.number="oportunidade.valor_estimado" placeholder="0.00" />
            </div>
             <div class="form-group">
                <label for="fonte">Fonte da Oportunidade</label>
                <select id="fonte" v-model="oportunidade.fonte">
                    <option :value="null">-- Selecione --</option>
                    <option value="SITE">Site</option>
                    <option value="PORTAL_IMOVEIS">Portal de Imóveis</option>
                    <option value="INDICACAO">Indicação</option>
                    <option value="CLIENTE_EXISTENTE">Cliente Existente</option>
                    <option value="REDES_SOCIAIS">Redes Sociais</option>
                    <option value="TELEFONE">Telefone</option>
                    <option value="EMAIL">Email</option>
                    <option value="VISITA_PRESENCIAL">Visita Presencial</option>
                    <option value="OUTRO">Outro</option>
                </select>
            </div>
            <div class="form-group full-width">
              <label for="informacoes_adicionais">Observações / Detalhes</label>
              <textarea id="informacoes_adicionais" v-model="oportunidade.informacoes_adicionais" rows="4" placeholder="Detalhes sobre a necessidade do cliente, preferências, etc."></textarea>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'A guardar...' : (isEditing ? 'Atualizar Oportunidade' : 'Criar Oportunidade') }}
            </button>
          </div>
        </form>
      </div> <div class="right-column" v-if="isEditing">
            <ClienteAtividades :oportunidadeId="oportunidadeId ? parseInt(oportunidadeId) : undefined" />

            <div class="card tarefas-card">
                 <h3 class="card-title">Tarefas Agendadas</h3>
                <button @click="abrirModalNovaTarefa" class="btn-nova-tarefa">
                    <i class="fas fa-plus"></i> Nova Tarefa
                </button>
                <div v-if="tarefas.length === 0" class="empty-state">
                    Nenhuma tarefa agendada para esta oportunidade.
                </div>
                 <ul v-else class="tarefas-list">
                     <li v-for="tarefa in tarefas" :key="tarefa.id" :class="['tarefa-item', { concluida: tarefa.concluida }]">
                        <div class="tarefa-info">
                            <span class="tarefa-titulo">{{ tarefa.titulo }}</span>
                            <span class="tarefa-data">
                                <i class="fas fa-calendar-alt"></i> {{ formatarDataHora(tarefa.data_agendada) }}
                            </span>
                            <span v-if="tarefa.responsavel_detalhes" class="tarefa-responsavel">
                                <i class="fas fa-user-tie"></i> {{ tarefa.responsavel_detalhes.first_name }}
                            </span>
                        </div>
                        <div class="tarefa-actions">
                             <button @click="toggleConcluirTarefa(tarefa)" :class="['btn-toggle-status', tarefa.concluida ? 'btn-toggle-status-reopen' : 'btn-toggle-status-done']" :title="tarefa.concluida ? 'Marcar como Pendente' : 'Marcar como Concluída'">
                                <i :class="['fas', tarefa.concluida ? 'fa-undo' : 'fa-check']"></i>
                            </button>
                            <button @click="abrirModalEditarTarefa(tarefa)" class="btn-edit-tarefa" title="Editar Tarefa">
                                <i class="fas fa-edit"></i>
                            </button>
                         </div>
                     </li>
                 </ul>
            </div>
        </div> </div> <TarefaModal
        v-if="showTarefaModal"
        :tarefa-id="tarefaParaEditarId"
        :oportunidade-id="oportunidadeId ? parseInt(oportunidadeId) : undefined"
        @close="fecharModalTarefa"
        @saved="tarefaSalva"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';
import ClienteAtividades from '@/components/ClienteAtividades.vue'; // Componente de histórico
import TarefaModal from '@/components/TarefaModal.vue'; // Modal para criar/editar tarefas
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';


// Interfaces (ajuste conforme necessário)
interface ClienteSelecao {
  id: number;
  nome_completo?: string;
  razao_social?: string;
  nome_identificacao?: string; // Propriedade computada para v-select
}

interface ImovelSelecao {
  id: number;
  codigo_referencia?: string;
  titulo_anuncio?: string;
  titulo_codigo?: string; // Propriedade computada para v-select
}

interface UserSelecao {
  id: number;
  first_name: string;
  last_name?: string;
}

interface FaseFunilSelecao {
  id: number;
  nome: string;
}
interface Tarefa {
    id: number;
    titulo: string;
    descricao: string;
    data_agendada: string;
    concluida: boolean;
    data_conclusao?: string | null;
    observacoes_finalizacao?: string;
    responsavel: number;
    responsavel_detalhes?: UserSelecao; // Adicionado para exibir nome
    oportunidade: number;
}


const route = useRoute();
const router = useRouter();

const oportunidadeId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!oportunidadeId.value);
const isLoadingData = ref(false);
const isSubmitting = ref(false);

const clientes = ref<ClienteSelecao[]>([]);
const imoveis = ref<ImovelSelecao[]>([]);
const corretores = ref<UserSelecao[]>([]);
const fasesFunil = ref<FaseFunilSelecao[]>([]);
const tarefas = ref<Tarefa[]>([]); // Lista de tarefas da oportunidade

// Estado do modal de tarefas
const showTarefaModal = ref(false);
const tarefaParaEditarId = ref<number | null>(null);

const oportunidade = ref({
  id: null,
  titulo: '',
  cliente_id: null,
  imovel_interesse_id: null,
  fase_funil_id: null,
  responsavel_id: null,
  valor_estimado: null,
  fonte: null,
  informacoes_adicionais: '',
});

// Funções de busca assíncrona para v-select
let clienteSearchTimeout: NodeJS.Timeout | null = null;
async function onClienteSearch(search: string, loading: (l: boolean) => void) {
    if (search.length >= 3) {
        if (clienteSearchTimeout) clearTimeout(clienteSearchTimeout);
        loading(true);
        clienteSearchTimeout = setTimeout(async () => {
            try {
                const response = await apiClient.get<ClienteSelecao[]>(`/v1/clientes/?search=${search}`);
                 // Adiciona a propriedade computada para exibição
                clientes.value = response.data.map(c => ({
                    ...c,
                    nome_identificacao: c.nome_completo || c.razao_social || 'Cliente sem nome'
                }));
            } catch (error) {
                console.error("Erro ao buscar clientes:", error);
                clientes.value = []; // Limpa em caso de erro
            } finally {
                loading(false);
            }
        }, 500); // Debounce de 500ms
    } else {
        // Opcional: Limpar resultados se a busca for muito curta
        // clientes.value = [];
    }
}


let imovelSearchTimeout: NodeJS.Timeout | null = null;
async function onImovelSearch(search: string, loading: (l: boolean) => void) {
     if (search.length >= 2) { // Busca a partir de 2 caracteres para código ou título
        if (imovelSearchTimeout) clearTimeout(imovelSearchTimeout);
        loading(true);
        imovelSearchTimeout = setTimeout(async () => {
            try {
                const response = await apiClient.get<ImovelSelecao[]>(`/v1/imoveis/?search=${search}`);
                // Adiciona a propriedade computada para exibição
                imoveis.value = response.data.map(i => ({
                    ...i,
                    titulo_codigo: `${i.titulo_anuncio || 'Imóvel'} (${i.codigo_referencia || 'S/Cód.'})`
                }));
            } catch (error) {
                console.error("Erro ao buscar imóveis:", error);
                imoveis.value = [];
            } finally {
                loading(false);
            }
        }, 500); // Debounce
    } else {
        // imoveis.value = [];
    }
}


// Carregar dados iniciais (corretores, fases) e dados da oportunidade se estiver editando
async function loadInitialData() {
  isLoadingData.value = true;
  try {
    const promises = [
      apiClient.get<UserSelecao[]>('/v1/core/usuarios/?cargo=Corretor'),
      apiClient.get<FaseFunilSelecao[]>('/v1/clientes/fases-funil/')
    ];

    if (isEditing.value && oportunidadeId.value) {
      promises.push(apiClient.get(`/v1/clientes/oportunidades/${oportunidadeId.value}/`));
      promises.push(apiClient.get<Tarefa[]>(`/v1/clientes/tarefas/?oportunidade=${oportunidadeId.value}`)); // Busca tarefas
    } else {
        // Se está criando, busca clientes e imóveis iniciais (ou deixa vazio)
        // promises.push(apiClient.get<ClienteSelecao[]>('/v1/clientes/?limit=10'));
        // promises.push(apiClient.get<ImovelSelecao[]>('/v1/imoveis/?limit=10'));
    }

    const results = await Promise.all(promises);

    corretores.value = results[0].data;
    fasesFunil.value = results[1].data.sort((a, b) => a.ordem - b.ordem); // Ordena fases

    if (isEditing.value && results.length > 2) {
      const opData = results[2].data;
       // Preenche o v-select com o cliente e imóvel atuais para exibição inicial
        if (opData.cliente_detalhes) {
            clientes.value = [{
                ...opData.cliente_detalhes,
                nome_identificacao: opData.cliente_detalhes.nome_completo || opData.cliente_detalhes.razao_social || ''
            }];
        }
        if (opData.imovel_detalhes) {
             imoveis.value = [{
                 ...opData.imovel_detalhes,
                 titulo_codigo: `${opData.imovel_detalhes.titulo_anuncio || 'Imóvel'} (${opData.imovel_detalhes.codigo_referencia || 'S/Cód.'})`
             }];
        }

      oportunidade.value = {
        id: opData.id,
        titulo: opData.titulo,
        cliente_id: opData.cliente, // API retorna o ID
        imovel_interesse_id: opData.imovel_interesse || null, // API retorna o ID
        fase_funil_id: opData.fase_funil, // API retorna o ID
        responsavel_id: opData.responsavel || null, // API retorna o ID
        valor_estimado: opData.valor_estimado ? parseFloat(opData.valor_estimado) : null,
        fonte: opData.fonte || null,
        informacoes_adicionais: opData.informacoes_adicionais || '',
      };

      if (results.length > 3) {
          tarefas.value = results[3].data; // Carrega tarefas
      }


    } else if (!isEditing.value && results.length > 2) {
        // clientes.value = results[2]?.data.map((c: ClienteSelecao) => ({...c, nome_identificacao: c.nome_completo || c.razao_social || ''})) || [];
        // imoveis.value = results[3]?.data.map((i: ImovelSelecao) => ({...i, titulo_codigo: `${i.titulo_anuncio || 'Imóvel'} (${i.codigo_referencia || 'S/Cód.'})`})) || [];
        // Se for criação, define a primeira fase como padrão
         if (fasesFunil.value.length > 0) {
            oportunidade.value.fase_funil_id = fasesFunil.value[0].id;
         }
    }


  } catch (error) {
    console.error('Erro ao carregar dados:', error);
    // Tratar erro (ex: exibir mensagem)
  } finally {
    isLoadingData.value = false;
  }
}

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    const payload = {
        titulo: oportunidade.value.titulo,
        cliente: oportunidade.value.cliente_id,
        imovel_interesse: oportunidade.value.imovel_interesse_id,
        fase_funil: oportunidade.value.fase_funil_id,
        responsavel: oportunidade.value.responsavel_id,
        valor_estimado: oportunidade.value.valor_estimado,
        fonte: oportunidade.value.fonte,
        informacoes_adicionais: oportunidade.value.informacoes_adicionais
    };

    let response;
    if (isEditing.value && oportunidadeId.value) {
      response = await apiClient.patch(`/v1/clientes/oportunidades/${oportunidadeId.value}/`, payload);
    } else {
      response = await apiClient.post('/v1/clientes/oportunidades/', payload);
    }

     if (response.data) {
        alert(`Oportunidade ${isEditing.value ? 'atualizada' : 'criada'} com sucesso!`);
        // Emitir evento para fechar modal ou redirecionar
        // Exemplo: Se for modal: emit('saved');
        // Exemplo: Se for página: router.push('/funil-vendas');
         if (route.meta.isModal) { // Verifica se está sendo usado como modal
             emit('saved');
         } else {
             router.push('/funil-vendas'); // Redireciona se for página
         }
     }

  } catch (error: any) {
    console.error("Erro ao guardar oportunidade:", error.response?.data || error);
    alert('Ocorreu um erro ao guardar a oportunidade.');
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
   if (route.meta.isModal) { // Verifica se está sendo usado como modal
        emit('close');
   } else {
        router.push('/funil-vendas'); // Redireciona se for página
   }
}

// Funções relacionadas a Tarefas
function abrirModalNovaTarefa() {
    tarefaParaEditarId.value = null; // Garante que é nova tarefa
    showTarefaModal.value = true;
}

function abrirModalEditarTarefa(tarefa: Tarefa) {
    tarefaParaEditarId.value = tarefa.id;
    showTarefaModal.value = true;
}

function fecharModalTarefa() {
    showTarefaModal.value = false;
    tarefaParaEditarId.value = null; // Limpa ID ao fechar
}

function tarefaSalva() {
    fecharModalTarefa();
    fetchTarefas(); // Recarrega a lista de tarefas
}

async function fetchTarefas() {
    if (!oportunidadeId.value) return;
    try {
        const response = await apiClient.get<Tarefa[]>(`/v1/clientes/tarefas/?oportunidade=${oportunidadeId.value}`);
        tarefas.value = response.data;
    } catch (error) {
        console.error("Erro ao buscar tarefas:", error);
    }
}

async function toggleConcluirTarefa(tarefa: Tarefa) {
    const novaConcluidaStatus = !tarefa.concluida;
    const observacao = novaConcluidaStatus
        ? prompt("Adicionar observação de finalização (opcional):", tarefa.observacoes_finalizacao || '')
        : null; // Não pede observação ao reabrir

    // Se o usuário cancelar o prompt ao concluir, não faz nada
    if (novaConcluidaStatus && observacao === null) {
        return;
    }

    try {
        const payload: { concluida: boolean; observacoes_finalizacao?: string | null } = {
            concluida: novaConcluidaStatus,
        };
        if (novaConcluidaStatus) {
            payload.observacoes_finalizacao = observacao;
        } else {
            // Ao reabrir, limpa a data de conclusão e observações
             payload.observacoes_finalizacao = null; // Define como null explicitamente se a API esperar
        }

        await apiClient.patch(`/v1/clientes/tarefas/${tarefa.id}/`, payload);
        // Atualiza localmente ou refaz o fetch
        // fetchTarefas(); // Mais simples refazer o fetch
         const index = tarefas.value.findIndex(t => t.id === tarefa.id);
         if (index !== -1) {
             tarefas.value[index].concluida = novaConcluidaStatus;
             tarefas.value[index].observacoes_finalizacao = novaConcluidaStatus ? observacao || undefined : undefined;
             tarefas.value[index].data_conclusao = novaConcluidaStatus ? new Date().toISOString() : null; // Atualiza data localmente
         }


    } catch (error) {
        console.error("Erro ao atualizar status da tarefa:", error);
        alert("Não foi possível atualizar o status da tarefa.");
    }
}


function formatarDataHora(dataIso: string | null): string {
  if (!dataIso) return 'N/A';
  try {
    // Formata data e hora
    return format(new Date(dataIso), 'dd/MM/yyyy HH:mm', { locale: ptBR });
  } catch {
    return 'Inválido';
  }
}


onMounted(loadInitialData);

// Define emits para comunicação se usado como modal
const emit = defineEmits(['close', 'saved']);
</script>

<style scoped>
.page-container {
  /* padding: 1.5rem; */ /* Removido */
  padding: 0; /* Adicionado */
  background-color: #f8f9fa; /* Fundo suave */
}

/* Regra .view-header removida */

.loading-message {
  text-align: center;
  padding: 2rem;
  font-size: 1.1rem;
  color: #6c757d;
}

.main-content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr; /* Coluna esquerda maior */
  gap: 1.5rem;
  align-items: start; /* Alinha os cards no topo */
}

/* Em telas menores, as colunas ficam empilhadas */
@media (max-width: 992px) {
  .main-content-grid {
    grid-template-columns: 1fr; /* Uma coluna */
  }
  .right-column {
      margin-top: 1.5rem; /* Espaço quando empilhado */
  }
}


.card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  padding: 1.5rem 2rem; /* Aumenta o padding */
  margin-bottom: 1.5rem; /* Espaço abaixo dos cards */
}
.card:last-child {
    margin-bottom: 0;
}

.card-title {
  font-size: 1.2rem; /* Aumenta o título do card */
  font-weight: 600;
  color: #343a40;
  margin-top: 0;
  margin-bottom: 1.5rem; /* Mais espaço abaixo do título */
  padding-bottom: 0.8rem;
  border-bottom: 1px solid #e9ecef;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); /* Grid responsivo */
  gap: 1.2rem 1.5rem; /* Espaço vertical e horizontal */
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1; /* Ocupa toda a largura */
}

label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.9rem;
  color: #495057;
}

input[type="text"],
input[type="number"],
input[type="email"], /* Adicionado */
select,
textarea,
:deep(.vs__dropdown-toggle) { /* Estilo para vue-select */
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  background-color: #fff; /* Garante fundo branco */
  height: auto; /* Garante altura automática para vue-select */
}
/* Ajuste específico para input dentro do vue-select */
:deep(.vs__search) {
    padding: 0 !important; /* Remove padding interno do input de busca */
    margin: 0 !important;
    border: none !important;
    font-family: inherit !important;
    font-size: inherit !important;
    height: auto !important;
}


input:focus,
select:focus,
textarea:focus,
:deep(.vs--open .vs__dropdown-toggle) { /* Foco para vue-select */
  border-color: #86b7fe;
  outline: 0;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

textarea {
  resize: vertical;
  min-height: 100px;
}

/* Estilos específicos vue-select */
:deep(.vs__dropdown-menu) {
    border-radius: 6px;
    border: 1px solid #ced4da;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
:deep(.vs__option) {
    padding: 0.75rem;
    font-size: 0.95rem;
}
:deep(.vs__option--highlight) {
    background-color: #0d6efd;
    color: white;
}
:deep(.vs__clear), :deep(.vs__open-indicator) {
    fill: #6c757d; /* Cor dos ícones */
}

/* Estilos para v-select quando desabilitado (se necessário) */
/*
:deep(.vs--disabled .vs__dropdown-toggle),
:deep(.vs--disabled .vs__search) {
    background-color: #e9ecef;
    cursor: not-allowed;
}
*/


.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem; /* Espaço acima dos botões */
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef; /* Linha divisória */
}

.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 500;
  transition: background-color 0.2s ease;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
}
.btn-primary { background-color: #0d6efd; color: white; }
.btn-primary:hover { background-color: #0b5ed7; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-secondary:hover { background-color: #5c636a; }
.btn-primary:disabled, .btn-secondary:disabled {
    background-color: #ced4da;
    cursor: not-allowed;
}

/* Coluna Direita - Tarefas e Atividades */
.right-column .card {
    margin-bottom: 1.5rem;
}

/* Tarefas Card */
.tarefas-card .card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.btn-nova-tarefa {
    background: none;
    border: 1px dashed #007bff;
    color: #007bff;
    padding: 8px 15px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: background-color 0.2s, color 0.2s;
    margin-bottom: 1rem; /* Espaço abaixo */
}
.btn-nova-tarefa:hover {
    background-color: #e7f1ff;
}
.btn-nova-tarefa i {
    margin-right: 5px;
}

.empty-state {
    text-align: center;
    color: #6c757d;
    font-size: 0.9rem;
    padding: 1.5rem 0;
}

.tarefas-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.tarefa-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 0;
    border-bottom: 1px solid #eee;
    transition: background-color 0.2s;
}
.tarefa-item:last-child {
    border-bottom: none;
}
.tarefa-item:hover {
    background-color: #f8f9fa; /* Leve destaque no hover */
}

.tarefa-item.concluida .tarefa-titulo {
    text-decoration: line-through;
    color: #6c757d;
}
.tarefa-item.concluida .tarefa-data,
.tarefa-item.concluida .tarefa-responsavel {
     color: #adb5bd;
}


.tarefa-info {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
}

.tarefa-titulo {
    font-weight: 500;
    color: #333;
    font-size: 0.95rem;
}

.tarefa-data, .tarefa-responsavel {
    font-size: 0.8rem;
    color: #6c757d;
    display: flex;
    align-items: center;
    gap: 0.3rem;
}
.tarefa-data i, .tarefa-responsavel i {
    color: #adb5bd;
}

.tarefa-actions {
  display: flex;
  gap: 0.5rem; /* Espaço entre os botões */
  align-items: center;
}

/* Botões de Ação da Tarefa */
.btn-toggle-status, .btn-edit-tarefa {
  padding: 6px 10px; /* Menor padding */
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.8rem; /* Menor fonte */
  font-weight: 500;
  transition: background-color 0.2s, transform 0.1s;
  line-height: 1; /* Garante que o ícone fique centralizado */
}
.btn-toggle-status i, .btn-edit-tarefa i {
    font-size: 0.9em; /* Tamanho do ícone relativo ao botão */
}

.btn-toggle-status-done {
  background-color: #d1e7dd; /* Verde claro */
  color: #198754;
}
.btn-toggle-status-done:hover {
  background-color: #badbcc;
}

.btn-toggle-status-reopen {
  background-color: #fff3cd; /* Amarelo claro */
  color: #ffc107;
}
.btn-toggle-status-reopen:hover {
  background-color: #ffeeba;
}

.btn-edit-tarefa {
  background-color: #cfe2ff; /* Azul claro */
  color: #0d6efd;
}
.btn-edit-tarefa:hover {
  background-color: #b6d4fe;
}


/* Estilos para links dentro do #no-options do v-select */
:deep(.vs__no-options a) {
    color: #007bff;
    text-decoration: underline;
    margin-left: 5px;
}
:deep(.vs__no-options a:hover) {
    color: #0056b3;
}

</style>
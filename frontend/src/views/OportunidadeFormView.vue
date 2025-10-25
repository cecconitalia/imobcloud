<template>
  <div class="page-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Oportunidade' : 'Adicionar Nova Oportunidade' }}</h1>
    </header>

    <div class="main-content-grid">
      <div class="left-column">
        <div v-if="isLoadingData" class="loading-message card">
          A carregar dados...
        </div>

        <form v-else @submit.prevent="handleSubmit" class="oportunidade-form card">
          <h3 class="card-title">Detalhes da Oportunidade</h3>
          <div class="form-grid">
            <div class="form-group full-width">
              <label for="titulo">Título da Oportunidade</label>
              <input type="text" id="titulo" v-model="oportunidade.titulo" placeholder="Ex: Venda do apartamento X para o cliente Y" required />
            </div>
            <div class="form-group">
              <label for="cliente">Cliente</label>
              <v-select
                id="cliente"
                label="nome_completo"
                :options="clientes"
                :reduce="cliente => cliente.id"
                v-model="oportunidade.cliente_id"
                placeholder="Digite para buscar um cliente"
                required
              >
                <template #no-options>
                  Nenhum cliente encontrado.
                </template>
              </v-select>
            </div>
            <div class="form-group">
              <label for="imovel">Imóvel de Interesse (opcional)</label>
              <v-select
                id="imovel"
                label="titulo_anuncio"
                :options="imoveis"
                :reduce="imovel => imovel.id"
                v-model="oportunidade.imovel_id"
                placeholder="Digite para buscar um imóvel"
              >
                <template #option="option">
                  <strong>{{ option.titulo_anuncio }}</strong><br>
                  <small>{{ option.logradouro }}</small>
                </template>
                <template #no-options>
                  Nenhum imóvel encontrado.
                </template>
              </v-select>
            </div>
            <div class="form-group">
              <label for="valor_estimado">Valor Estimado (R$)</label>
              <input type="number" step="0.01" id="valor_estimado" v-model="oportunidade.valor_estimado" />
            </div>
            <div class="form-group">
              <label for="fonte">Fonte do Lead</label>
              <select id="fonte" v-model="oportunidade.fonte">
                <option :value="null">Não informada</option>
                <option value="SITE">Site</option>
                <option value="INDICACAO">Indicação</option>
                <option value="ANUNCIO">Anúncio Online</option>
                <option value="CLIENTE_ANTIGO">Cliente Antigo</option>
                <option value="OUTRO">Outro</option>
              </select>
            </div>
            <div class="form-group">
              <label for="probabilidade">Probabilidade de Fechamento (%)</label>
              <input type="number" id="probabilidade" v-model="oportunidade.probabilidade" min="0" max="100" />
            </div>
            <div class="form-group">
              <label for="responsavel">Corretor Responsável</label>
              <select id="responsavel" v-model="oportunidade.responsavel_id" disabled>
                <option :value="null">Ninguém</option>
                <option v-for="corretor in corretores" :key="corretor.id" :value="corretor.id">
                  {{ corretor.first_name || corretor.username }}
                </option>
              </select>
            </div>
          </div>
          <div class="form-group textarea-group">
            <label for="informacoes_adicionais">Informações Adicionais (opcional)</label>
            <textarea id="informacoes_adicionais" v-model="oportunidade.informacoes_adicionais" rows="3" placeholder="Insira notas importantes sobre a oportunidade..."></textarea>
          </div>
          <div v-if="oportunidade.fase === 'PERDIDO'" class="form-group textarea-group">
            <label for="motivo_perda">Motivo da Perda</label>
            <textarea id="motivo_perda" v-model="oportunidade.motivo_perda" rows="3" placeholder="Descreva por que este negócio foi perdido..."></textarea>
          </div>
          <div class="form-actions">
            <router-link v-if="isEditing && oportunidade.cliente_id" :to="{ name: 'cliente-editar', params: { id: oportunidade.cliente_id } }" class="btn btn-info">
              Ver Histórico do Cliente
            </router-link>
            <button type="button" @click="handleCancel" class="btn btn-secondary">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? 'A Guardar...' : (isEditing ? 'Guardar Alterações' : 'Criar Oportunidade') }}
            </button>
          </div>
        </form>
      </div>

      <div class="right-column">
        <div v-if="isEditing" class="phase-selector-container">
          <div class="card phase-card">
            <FaseSelector
              :current-fase-id="oportunidade.fase"
              @update:fase="handleFaseUpdate"
            />
          </div>
        </div>
        
        <div v-if="isEditing" class="transferir-container">
          <div class="card">
            <OportunidadeTransferir
              :oportunidade-id="oportunidadeId"
              :corretor-responsavel-id="oportunidade.responsavel_id"
              @transferido="handleTransferenciaConcluida"
            />
          </div>
        </div>

        <div class="tarefas-container card">
          <div class="tarefas-header">
            <h3 class="card-title">Tarefas Agendadas</h3>
            <button @click="showTarefaModal(oportunidade)" class="btn btn-add-tarefa">+ Adicionar Tarefa</button>
          </div>
          <div v-if="isLoadingTarefas" class="loading-message">A carregar tarefas...</div>
          <div v-else-if="sortedTarefas && sortedTarefas.length === 0" class="no-tasks-message">
            Nenhuma tarefa agendada.
          </div>
          <ul v-else class="tarefas-list">
            <li v-for="tarefa in sortedTarefas" :key="tarefa.id" :class="['tarefa-card', { 'tarefa-concluida': tarefa.concluida }]">
              <div class="tarefa-card-content">
                <div class="tarefa-status">
                  <span v-if="tarefa.concluida" class="icon-concluida">✔</span>
                  <span v-else class="icon-pendente">○</span>
                </div>
                <div class="tarefa-details">
                  <h4 :class="{ 'text-strike': tarefa.concluida }">{{ tarefa.titulo }}</h4>
                  <p v-if="tarefa.descricao" :class="{ 'text-strike': tarefa.concluida }">{{ tarefa.descricao }}</p>
                  <span class="tarefa-data" v-if="tarefa.data_vencimento">
                    Prazo: {{ formatarData(tarefa.data_vencimento) }}
                  </span>
                </div>
              </div>
              <div class="tarefa-actions">
                <button
                  @click="toggleConcluida(tarefa)"
                  :class="['btn', 'btn-toggle-status', { 'btn-toggle-status-done': !tarefa.concluida, 'btn-toggle-status-reopen': tarefa.concluida }]"
                >
                  {{ tarefa.concluida ? 'Reabrir' : 'Finalizar' }}
                </button>
                <button @click="showTarefaModal(oportunidade, tarefa)" class="btn btn-edit-tarefa">Editar</button>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
    
  <TarefaModal
    v-if="tarefaModal.visible"
    :oportunidade-id="oportunidadeId"
    :tarefa-para-editar="tarefaModal.tarefa"
    :oportunidade-inicial="oportunidadeModalData"
    @close="closeTarefaModal"
    @saved="handleTarefaSalva"
  />
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import OportunidadeTransferir from '@/components/OportunidadeTransferir.vue';
import TarefaModal from '@/components/TarefaModal.vue';
import FaseSelector from '@/components/FaseSelector.vue';
import vSelect from 'vue-select';
import 'vue-select/dist/vue-select.css';

const router = useRouter();
const route = useRoute();

const oportunidadeId = computed(() => route.params.id as string | undefined);
const isEditing = computed(() => !!oportunidadeId.value);

const oportunidade = ref({
  titulo: '',
  cliente_id: null as number | null,
  imovel_id: null as number | null,
  responsavel_id: null as number | null,
  valor_estimado: null,
  fase: 'LEAD',
  fonte: null,
  probabilidade: 10,
  motivo_perda: '',
  informacoes_adicionais: '',
  tarefas: [] as any[],
});

const clientes = ref<any[]>([]);
const imoveis = ref<any[]>([]);
const corretores = ref<any[]>([]);
const isLoadingData = ref(true);
const isSubmitting = ref(false);
const tarefaModal = ref({ visible: false, tarefa: null as any });
const oportunidadeModalData = ref<any>(null);
const isLoadingTarefas = ref(false);

const sortedTarefas = computed(() => {
  if (!oportunidade.value.tarefas) return [];
  const tarefasPendentes = oportunidade.value.tarefas
    .filter(t => !t.concluida)
    .sort((a, b) => new Date(a.data_vencimento).getTime() - new Date(b.data_vencimento).getTime());
  
  const tarefasConcluidas = oportunidade.value.tarefas
    .filter(t => t.concluida)
    .sort((a, b) => new Date(b.data_vencimento).getTime() - new Date(a.data_vencimento).getTime());

  return [...tarefasPendentes, ...tarefasConcluidas];
});

async function fetchData() {
  isLoadingData.value = true;
  try {
    const [clientesResponse, imoveisResponse, corretoresResponse] = await Promise.all([
      apiClient.get('/v1/clientes/'),
      apiClient.get('/v1/imoveis/'),
      apiClient.get('/v1/corretores/')
    ]);
    clientes.value = clientesResponse.data;
    imoveis.value = imoveisResponse.data;
    corretores.value = corretoresResponse.data;

    if (isEditing.value) {
      const oportunidadeResponse = await apiClient.get(`/v1/oportunidades/${oportunidadeId.value}/`);
      
      const data = oportunidadeResponse.data;
      oportunidade.value = {
        ...data,
        cliente_id: data.cliente?.id || null,
        imovel_id: data.imovel?.id || null,
        responsavel_id: data.responsavel?.id || null,
      };
    }
  } catch (error) {
    console.error("Erro ao carregar dados:", error);
    alert('Não foi possível carregar os dados necessários.');
  } finally {
    isLoadingData.value = false;
  }
}

async function handleFaseUpdate(novaFaseId: string) {
  try {
    await apiClient.patch(`/v1/oportunidades/${oportunidadeId.value}/`, {
      fase: novaFaseId,
    });
    oportunidade.value.fase = novaFaseId;
  } catch (error) {
    console.error('Erro ao atualizar a fase:', error);
    alert('Não foi possível atualizar a fase da oportunidade.');
  }
}

async function handleTarefaSalva() {
  closeTarefaModal();
  await fetchData(); 
}

function showTarefaModal(oportunidadeAtual: any = null, tarefa = null) {
  oportunidadeModalData.value = oportunidadeAtual;
  tarefaModal.value.tarefa = tarefa;
  tarefaModal.value.visible = true;
}

function closeTarefaModal() {
  tarefaModal.value.visible = false;
  tarefaModal.value.tarefa = null;
  oportunidadeModalData.value = null;
}

async function toggleConcluida(tarefa: any) {
  const newStatus = !tarefa.concluida;
  try {
    await apiClient.patch(`/v1/tarefas/${tarefa.id}/`, {
      concluida: newStatus,
    });
    tarefa.concluida = newStatus;
  } catch (error) {
    console.error("Erro ao atualizar status da tarefa:", error);
    alert('Não foi possível atualizar o status da tarefa.');
  }
}

function handleTransferenciaConcluida() {
  alert('Oportunidade transferida com sucesso!');
  fetchData();
}

onMounted(() => {
  fetchData();
});

function formatarData(data: string) {
  if (!data) return '';
  const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
  return new Date(data).toLocaleString('pt-BR', options);
}

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    const payload = {
        titulo: oportunidade.value.titulo,
        fase: oportunidade.value.fase,
        valor_estimado: oportunidade.value.valor_estimado,
        fonte: oportunidade.value.fonte,
        probabilidade: oportunidade.value.probabilidade,
        motivo_perda: oportunidade.value.motivo_perda,
        informacoes_adicionais: oportunidade.value.informacoes_adicionais,
        cliente: oportunidade.value.cliente_id,
        imovel: oportunidade.value.imovel_id,
    };

    if (isEditing.value) {
      await apiClient.put(`/v1/oportunidades/${oportunidadeId.value}/`, payload);
    } else {
      await apiClient.post('/v1/oportunidades/', payload);
    }
    router.push({ name: 'funil-vendas' });
  } catch (error: any) {
    console.error("Erro ao guardar oportunidade:", error.response?.data || error);
    alert(`Ocorreu um erro ao guardar a oportunidade: ${JSON.stringify(error.response?.data)}`);
  } finally {
    isSubmitting.value = false;
  }
}

function handleCancel() {
  router.push({ name: 'funil-vendas' });
}
</script>

<style scoped>
/* Estilos gerais da página */
.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #333;
}
.view-header {
  margin-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 1rem;
}
h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}
.main-content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}
@media (max-width: 1024px) {
  .main-content-grid {
    grid-template-columns: 1fr;
  }
}
.left-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.right-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Estilos de Cartão (Card) */
.card {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e0e0;
}
.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 1rem;
}

/* Seletor de Fase */
.phase-selector-container {
  order: -1;
}
.phase-card {
  padding: 1.5rem;
}

/* Formulário Principal */
.oportunidade-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  flex-grow: 1;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}
@media (max-width: 768px) {
  .oportunidade-form .form-grid {
    grid-template-columns: 1fr;
  }
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group.full-width {
  grid-column: 1 / -1;
}
.form-group.textarea-group {
  grid-column: 1 / -1;
}
.form-group.placeholder-group {
  visibility: hidden;
}
label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
  font-size: 0.9rem;
}
input, select, textarea {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  background-color: #f9fafb;
  transition: border-color 0.2s, box-shadow 0.2s;
}
input:focus, select:focus, textarea:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
  outline: none;
}
textarea {
  resize: vertical;
  min-height: 80px;
}
:deep(.vs__dropdown-toggle) {
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  background-color: #f9fafb;
  height: 40px;
}
:deep(.vs__dropdown-toggle.vs--open) {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
}
:deep(.vs__selected) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  width: 100%;
  margin-top: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

/* Botões */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s, transform 0.1s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-primary:hover {
  background-color: #0056b3;
}
.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}
.btn-secondary:hover {
  background-color: #5a6268;
}
.btn-info {
  background-color: #17a2b8;
  color: white;
}
.btn-info:hover {
  background-color: #138496;
}

/* Tarefas Agendadas */
.tarefas-container {
  margin-top: 0;
}
.tarefas-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.tarefas-header .card-title {
  margin-bottom: 0;
  border-bottom: none;
  padding-bottom: 0;
}
.btn-add-tarefa {
  background-color: #28a745;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}
.btn-add-tarefa:hover {
  background-color: #218838;
}
.tarefas-list {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}
.tarefa-card {
  background-color: #f8f9fa;
  padding: 1.25rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-left: 5px solid #007bff;
  transition: all 0.3s ease;
}
.tarefa-concluida {
  background-color: #e9ecef;
  border-left-color: #6c757d;
  opacity: 0.8;
}
.tarefa-card-content {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}
.tarefa-status {
  font-size: 1.5rem;
  line-height: 1;
  color: #007bff;
}
.tarefa-concluida .tarefa-status {
  color: #28a745;
}
.tarefa-details {
  flex-grow: 1;
}
.tarefa-details h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1rem;
  color: #333;
}
.tarefa-details p {
  margin: 0 0 0.5rem 0;
  font-size: 0.9rem;
  color: #555;
  line-height: 1.4;
}
.tarefa-data {
  font-size: 0.8rem;
  color: #777;
  display: block;
}
.tarefa-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
  border-top: 1px solid #eee;
  padding-top: 1rem;
}
.btn-toggle-status, .btn-edit-tarefa {
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background-color 0.2s, transform 0.1s;
}
.btn-toggle-status-done {
  background-color: #28a745;
  color: white;
}
.btn-toggle-status-done:hover {
  background-color: #218838;
}
.btn-toggle-status-reopen {
  background-color: #ffc107;
  color: #333;
}
.btn-toggle-status-reopen:hover {
  background-color: #e0a800;
}
.btn-edit-tarefa {
  background-color: #007bff;
  color: white;
}
.btn-edit-tarefa:hover {
  background-color: #0056b3;
}
.text-strike {
  text-decoration: line-through;
  color: #888;
}
.no-tasks-message {
  text-align: center;
  color: #6c757d;
  padding: 2rem;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-top: 1.5rem;
}
/* Responsividade */
@media (max-width: 1024px) {
  .main-content-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 768px) {
  .oportunidade-form .form-grid {
    grid-template-columns: 1fr;
  }
  .form-actions {
    flex-direction: column;
  }
  .btn {
    width: 100%;
  }
  .tarefas-list {
    grid-template-columns: 1fr;
  }
  .phase-selector-container,
  .oportunidade-form,
  .tarefas-container {
    padding: 1.5rem;
  }
}
</style>
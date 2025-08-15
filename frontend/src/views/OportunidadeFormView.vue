<template>
  <div class="form-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Oportunidade' : 'Adicionar Nova Oportunidade' }}</h1>
    </header>

    <div v-if="isEditing" class="phase-selector-wrapper">
      <FaseSelector
        :current-fase-id="oportunidade.fase"
        @update:fase="handleFaseUpdate"
      />
    </div>

    <div v-if="isLoadingData" class="loading-message">
      A carregar dados...
    </div>

    <form v-else @submit.prevent="handleSubmit" class="oportunidade-form">
      <div class="form-group full-width">
        <label for="titulo">Título da Oportunidade</label>
        <input type="text" id="titulo" v-model="oportunidade.titulo" placeholder="Ex: Venda do apartamento X para o cliente Y" required />
      </div>

      <div class="form-group">
        <label for="cliente">Cliente</label>
        <select id="cliente" v-model="oportunidade.cliente_id" required>
          <option disabled :value="null">Selecione um cliente</option>
          <option v-for="c in clientes" :key="c.id" :value="c.id">
            {{ c.nome_completo }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="imovel">Imóvel de Interesse (opcional)</label>
        <select id="imovel" v-model="oportunidade.imovel_id">
          <option :value="null">Nenhum</option>
          <option v-for="i in imoveis" :key="i.id" :value="i.id">
            {{ i.endereco }}
          </option>
        </select>
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

      <div v-if="oportunidade.fase === 'PERDIDO'" class="form-group full-width">
        <label for="motivo_perda">Motivo da Perda</label>
        <textarea id="motivo_perda" v-model="oportunidade.motivo_perda" rows="3" placeholder="Descreva por que este negócio foi perdido..."></textarea>
      </div>
      
      <div class="form-actions full-width">
        <router-link v-if="isEditing && oportunidade.cliente_id" :to="{ name: 'cliente-editar', params: { id: oportunidade.cliente_id } }" class="btn-info">
          Ver Histórico do Cliente
        </router-link>
        
        <button type="button" @click="handleCancel" class="btn-secondary">Cancelar</button>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'A Guardar...' : (isEditing ? 'Guardar Alterações' : 'Criar Oportunidade') }}
        </button>
      </div>
    </form>
    
    <OportunidadeTransferir
      v-if="isEditing"
      :oportunidade-id="oportunidadeId"
      :corretor-responsavel-id="oportunidade.responsavel_id"
      @transferido="handleTransferenciaConcluida"
    />

    <div v-if="isEditing" class="tarefas-container">
      <div class="tarefas-header">
        <h3>Tarefas Agendadas</h3>
        <button @click="showTarefaModal()" class="btn-primary-small">+ Adicionar Tarefa</button>
      </div>
      <div v-if="isLoadingTarefas" class="loading-message">A carregar tarefas...</div>
      <div v-else-if="oportunidade.tarefas && oportunidade.tarefas.length === 0" class="no-tasks-message">
        Nenhuma tarefa agendada.
      </div>
      <ul v-else class="tarefas-list">
        <li v-for="tarefa in oportunidade.tarefas" :key="tarefa.id" class="tarefa-item">
          <div class="tarefa-info">
            <input type="checkbox" :checked="tarefa.concluida" @change="toggleConcluida(tarefa)">
            <div class="tarefa-text-group">
              <span class="tarefa-descricao" :class="{ 'concluida': tarefa.concluida }">{{ tarefa.descricao }}</span>
              <span class="tarefa-data" v-if="tarefa.data_conclusao">Prazo: {{ formatarData(tarefa.data_conclusao) }}</span>
            </div>
          </div>
          <button @click="showTarefaModal(tarefa)" class="btn-secondary-small">Editar</button>
        </li>
      </ul>
    </div>
    
    <TarefaModal
      v-if="tarefaModal.visible"
      :oportunidade-id="oportunidadeId"
      :tarefa="tarefaModal.tarefa"
      @close="closeTarefaModal"
      @saved="handleTarefaSalva"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';
import OportunidadeTransferir from '@/components/OportunidadeTransferir.vue';
import TarefaModal from '@/components/TarefaModal.vue';
import FaseSelector from '@/components/FaseSelector.vue';

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
  data_proximo_contato: null,
  motivo_perda: '',
  tarefas: [] as any[],
});

const clientes = ref<any[]>([]);
const imoveis = ref<any[]>([]);
const corretores = ref<any[]>([]);
const isLoadingData = ref(true);
const isSubmitting = ref(false);
const tarefaModal = ref({ visible: false, tarefa: null as any });
const isLoadingTarefas = ref(false);

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

function showTarefaModal(tarefa = null) {
  tarefaModal.value.tarefa = tarefa;
  tarefaModal.value.visible = true;
}

function closeTarefaModal() {
  tarefaModal.value.visible = false;
  tarefaModal.value.tarefa = null;
}

async function toggleConcluida(tarefa: any) {
  const newStatus = !tarefa.concluida;
  try {
    await apiClient.patch(`/v1/atividades/${tarefa.id}/`, {
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
  const dataObj = new Date(data);
  return dataObj.toLocaleDateString('pt-BR');
}

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    // CORREÇÃO DEFINITIVA: Construímos um payload limpo apenas com os dados
    // que a API espera, garantindo que os campos de relacionamento enviem apenas o ID.
    const payload = {
        titulo: oportunidade.value.titulo,
        fase: oportunidade.value.fase,
        valor_estimado: oportunidade.value.valor_estimado,
        fonte: oportunidade.value.fonte,
        probabilidade: oportunidade.value.probabilidade,
        motivo_perda: oportunidade.value.motivo_perda,
        // O backend espera os campos 'cliente' e 'imovel' com os IDs.
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
/* Os seus estilos existentes permanecem inalterados */
.form-container { padding: 2rem; }
.view-header { margin-bottom: 1.5rem; }
.oportunidade-form { display: flex; flex-wrap: wrap; gap: 1.5rem; }
.form-group { display: flex; flex-direction: column; flex: 1 1 calc(50% - 1.5rem); }
.form-group.full-width { flex-basis: 100%; }
label { margin-bottom: 0.5rem; font-weight: bold; }
input, select, textarea { padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; width: 100%; margin-top: 1rem; }
.btn-primary, .btn-secondary, .btn-info { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
.btn-primary { background-color: #007bff; color: white; }
.btn-secondary { background-color: #6c757d; color: white; }
.btn-info { background-color: #17a2b8; color: white; text-decoration: none;}
.loading-message { text-align: center; padding: 2rem; }
.phase-selector-wrapper { margin-bottom: 2rem; padding-bottom: 2rem; border-bottom: 1px solid #e0e0e0; }
.tarefas-container { margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e0e0e0; }
.tarefas-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.tarefas-header h3 { margin: 0; }
.btn-primary-small { background-color: #007bff; color: white; padding: 8px 12px; border: none; border-radius: 5px; cursor: pointer; font-size: 0.9em; }
.tarefas-list { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 0.75rem; }
.tarefa-item { background-color: #f8f9fa; padding: 1rem; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
.tarefa-info { display: flex; align-items: center; gap: 1rem; }
.tarefa-text-group { display: flex; flex-direction: column; }
.tarefa-descricao { font-weight: bold; }
.tarefa-descricao.concluida { text-decoration: line-through; color: #6c757d; }
.tarefa-data { font-size: 0.9em; color: #6c757d; }
.no-tasks-message { text-align: center; color: #6c757d; padding: 2rem; }
.btn-secondary-small { background-color: #6c757d; color: white; padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; }
</style>
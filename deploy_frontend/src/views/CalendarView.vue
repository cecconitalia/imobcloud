<template>
  <div class="calendar-container">
    <header class="view-header">
      <h1>Meu Calendário de Tarefas</h1>
    </header>

    <div v-if="isLoading" class="loading-message">A carregar tarefas...</div>
    <div v-else-if="tarefas.length === 0" class="no-tasks-message">
      <p>Nenhuma tarefa agendada.</p>
    </div>

    <div v-else class="tasks-list">
      <div v-for="tarefa in tarefas" :key="tarefa.id" class="task-item" @click="showTarefaModal(tarefa)">
        <div class="task-info">
          <span class="task-date">{{ formatarData(tarefa.data_conclusao) }}</span>
          <h4 class="task-description">{{ tarefa.descricao }}</h4>
        </div>
        <div class="task-actions">
          <button @click.stop="marcarComoConcluida(tarefa)" class="btn-concluir" :disabled="isUpdating || tarefa.concluida">
            {{ tarefa.concluida ? 'Concluída' : 'Concluir' }}
          </button>
        </div>
      </div>
    </div>

    <TarefaModal
      v-if="tarefaModal.visible"
      :oportunidade-id="tarefaModal.tarefa.oportunidade"
      :tarefa="tarefaModal.tarefa"
      @close="closeTarefaModal"
      @saved="handleTarefaSalva"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
// Importa o componente modal de tarefas
import TarefaModal from '@/components/TarefaModal.vue';

const tarefas = ref<any[]>([]);
const isLoading = ref(true);
const isUpdating = ref(false);

const tarefaModal = ref({
  visible: false,
  tarefa: null as any,
});

async function fetchTarefas() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/clientes/minhas_tarefas/');
    tarefas.value = response.data;
  } catch (error) {
    console.error("Erro ao buscar tarefas:", error);
    alert('Não foi possível carregar as suas tarefas.');
  } finally {
    isLoading.value = false;
  }
}

async function marcarComoConcluida(tarefa: any) {
  if (tarefa.concluida) return;
  if (!window.confirm('Marcar esta tarefa como concluída?')) {
    return;
  }
  isUpdating.value = true;
  try {
    const payload = {
      concluida: true,
    };
    await apiClient.patch(`/v1/clientes/oportunidades/${tarefa.oportunidade}/tarefas/${tarefa.id}/`, payload);
    await fetchTarefas();
  } catch (error) {
    console.error("Erro ao concluir a tarefa:", error);
    alert('Ocorreu um erro ao concluir a tarefa.');
  } finally {
    isUpdating.value = false;
  }
}

function showTarefaModal(tarefa: any) {
  tarefaModal.value.tarefa = tarefa;
  tarefaModal.value.visible = true;
}

function closeTarefaModal() {
  tarefaModal.value.visible = false;
  tarefaModal.value.tarefa = null;
}

async function handleTarefaSalva() {
  closeTarefaModal();
  await fetchTarefas(); // Recarrega os dados após salvar
}

function formatarData(data: string) {
  if (!data) return 'Sem prazo';
  return new Date(data).toLocaleDateString('pt-BR');
}

onMounted(() => {
  fetchTarefas();
});
</script>

<style scoped>
.calendar-container {
  padding: 2rem;
}
.view-header {
  margin-bottom: 1.5rem;
}
.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.task-item {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer; /* Adiciona o cursor de clique */
}
.task-info {
  display: flex;
  flex-direction: column;
}
.task-date {
  font-size: 0.9em;
  color: #6c757d;
  margin-bottom: 0.5rem;
}
.task-description {
  margin: 0;
  font-size: 1rem;
  font-weight: bold;
}
.btn-concluir {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-concluir:disabled {
  background-color: #a3d9b1;
  cursor: not-allowed;
}
.loading-message, .no-tasks-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
</style>
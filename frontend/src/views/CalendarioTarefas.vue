<template>
  <div class="calendar-container">
    <header class="view-header">
      <h1>Meu Calendário de Tarefas</h1>
    </header>

    <div v-if="isLoading" class="loading-message">
      A carregar tarefas...
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else class="calendar-wrapper">
      <FullCalendar ref="fullCalendar" :options="calendarOptions" />
    </div>

    <div class="task-list-section">
      <div class="task-list-header">
        <h3>Próximas Tarefas</h3>
      </div>
      <div v-if="proximasTarefas.length > 0" class="task-list-wrapper">
        <ul class="task-list">
          <li v-for="tarefa in proximasTarefas" :key="tarefa.id" class="task-item">
            <span class="task-date">{{ formatarData(tarefa.data_conclusao) }}</span>
            <div class="task-info">
              <span class="task-description">{{ tarefa.descricao }}</span>
              <span class="task-oportunidade" v-if="tarefa.oportunidade_id">
                Oportunidade: #{{ tarefa.oportunidade_id }}
              </span>
            </div>
            <span class="task-status" :class="{ 'overdue': isOverdue(tarefa.data_conclusao) }">
              {{ isOverdue(tarefa.data_conclusao) ? 'Vencida' : 'Pendente' }}
            </span>
          </li>
        </ul>
      </div>
      <div v-else class="no-tasks-message">
        Nenhuma tarefa agendada para os próximos 30 dias.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import apiClient from '@/services/api';
import { useRouter } from 'vue-router';

const router = useRouter();

const isLoading = ref(true);
const error = ref<string | null>(null);
const tarefas = ref<any[]>([]);

const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  events: [] as any[],
  locale: 'pt-br',
  // CORREÇÃO: Ação no evento de clique
  eventClick: handleEventClick,
});

const proximasTarefas = ref<any[]>([]);

function formatarData(dataString: string) {
  const data = new Date(dataString);
  return data.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function isOverdue(dataString: string) {
  const data = new Date(dataString);
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  return data < hoje;
}

// CORREÇÃO: Nova lógica para redirecionar para a edição da tarefa
function handleEventClick(info: any) {
  const oportunidadeId = info.event.extendedProps.oportunidade_id;
  const tarefaId = info.event.extendedProps.id;
  if (oportunidadeId && tarefaId) {
    router.push({ 
      name: 'oportunidade-editar', 
      params: { id: oportunidadeId },
      query: { tarefaId: tarefaId }
    });
  } else {
    // Ação padrão se não houver oportunidade ou tarefa associada
    alert(`Tarefa: ${info.event.title}`);
  }
}

async function fetchTarefas() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/tarefas/');
    tarefas.value = response.data;
    
    calendarOptions.value.events = tarefas.value.map(tarefa => ({
      id: tarefa.id,
      title: tarefa.descricao,
      start: tarefa.data_conclusao,
      backgroundColor: tarefa.concluida ? '#28a745' : '#dc3545',
      extendedProps: {
        oportunidade_id: tarefa.oportunidade,
        id: tarefa.id,
        concluida: tarefa.concluida
      }
    }));

    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    const trintaDias = new Date(hoje);
    trintaDias.setDate(hoje.getDate() + 30);
    
    proximasTarefas.value = tarefas.value
      .filter(t => new Date(t.data_conclusao) >= hoje && new Date(t.data_conclusao) <= trintaDias && !t.concluida)
      .sort((a, b) => new Date(a.data_conclusao).getTime() - new Date(b.data_conclusao).getTime());
      
  } catch (err) {
    console.error("Erro ao buscar tarefas:", err);
    error.value = 'Não foi possível carregar as tarefas.';
  } finally {
    isLoading.value = false;
  }
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
.calendar-wrapper {
  background-color: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.loading-message, .error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
.task-list-section {
  margin-top: 2rem;
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.task-list-header h3 {
  margin-top: 0;
  border-bottom: 2px solid #007bff;
  padding-bottom: 0.5rem;
}
.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.task-item {
  display: flex;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #e9ecef;
}
.task-item:last-child {
  border-bottom: none;
}
.task-date {
  font-weight: bold;
  color: #007bff;
  flex-shrink: 0;
  margin-right: 1.5rem;
  width: 90px;
}
.task-info {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}
.task-description {
  font-weight: 500;
  color: #343a40;
}
.task-oportunidade {
  font-size: 0.85em;
  color: #6c757d;
}
.task-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
  background-color: #ffc107;
  white-space: nowrap;
}
.task-status.overdue {
  background-color: #dc3545;
}
.no-tasks-message {
  text-align: center;
  color: #6c757d;
  padding: 1rem;
}
</style>
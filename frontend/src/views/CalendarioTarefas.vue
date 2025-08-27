<template>
  <div class="calendar-container">
    <header class="view-header">
      <h1>Meu Calendário de Tarefas</h1>
    </header>

    <div class="calendar-wrapper">
      <FullCalendar ref="fullCalendar" :options="calendarOptions" />
    </div>

    <TarefaDetalhesModal
      v-if="isDetalhesModalVisible"
      :tarefa="tarefaSelecionada"
      @close="closeDetalhesModal"
      @edit="handleEdit"
      @saved="handleSaved"
    />

    <TarefaModal
      v-if="isEditModalVisible"
      :tarefaParaEditar="tarefaParaEditar"
      @close="closeEditModal"
      @saved="handleSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import ptBrLocale from '@fullcalendar/core/locales/pt-br';
import apiClient from '@/services/api';
import TarefaDetalhesModal from '@/components/calendario/TarefaDetalhesModal.vue';
import TarefaModal from '@/components/TarefaModal.vue';

// --- ESTADO ---
const fullCalendar = ref<any>(null);
const isDetalhesModalVisible = ref(false);
const isEditModalVisible = ref(false);
const tarefaSelecionada = ref<any | null>(null);
const tarefaParaEditar = ref<any | null>(null);

// --- FUNÇÕES ---
const fetchTarefasApi = async (fetchInfo: any, successCallback: any, failureCallback: any) => {
  try {
    const params = {
      start: fetchInfo.startStr,
      end: fetchInfo.endStr,
    };
    const response = await apiClient.get('/v1/tarefas/', { params });
    
    const eventos = response.data.map((tarefa: any) => ({
      id: tarefa.id,
      title: tarefa.titulo,
      start: tarefa.data_vencimento,
      end: tarefa.data_vencimento,
      backgroundColor: tarefa.concluida ? '#28a745' : '#007bff',
      borderColor: tarefa.concluida ? '#28a745' : '#007bff',
      extendedProps: {
        ...tarefa
      }
    }));
    
    successCallback(eventos);
  } catch (error) {
    console.error('Erro ao carregar tarefas:', error);
    failureCallback(error);
  }
};

// --- INÍCIO DA CORREÇÃO ---
const handleEventClick = (clickInfo: any) => {
  // Passamos apenas os dados da tarefa (extendedProps) para o modal de detalhes
  tarefaSelecionada.value = clickInfo.event.extendedProps;
  isDetalhesModalVisible.value = true;
};
// --- FIM DA CORREÇÃO ---

const closeDetalhesModal = () => {
  isDetalhesModalVisible.value = false;
  tarefaSelecionada.value = null;
};

const closeEditModal = () => {
  isEditModalVisible.value = false;
  tarefaParaEditar.value = null;
};

const handleEdit = (tarefa: any) => {
  closeDetalhesModal();
  tarefaParaEditar.value = tarefa;
  isEditModalVisible.value = true;
};

const handleSaved = () => {
    closeDetalhesModal();
    closeEditModal();
    if (fullCalendar.value) {
        fullCalendar.value.getApi().refetchEvents();
    }
};

const calendarOptions = reactive({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay'
  },
  editable: true,
  selectable: true,
  weekends: true,
  locale: ptBrLocale,
  events: fetchTarefasApi,
  eventClick: handleEventClick,
});
</script>

<style scoped>
.calendar-container { padding: 2rem; background-color: #f9f9f9; }
.view-header { margin-bottom: 1.5rem; }
.view-header h1 { font-size: 2.2rem; color: #333; }
.calendar-wrapper { background-color: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
:deep(.fc-button-primary) { background-color: #007bff; border-color: #007bff; }
:deep(.fc-button-primary:hover) { background-color: #0056b3; border-color: #0056b3; }
:deep(.fc-event) { cursor: pointer; }
</style>
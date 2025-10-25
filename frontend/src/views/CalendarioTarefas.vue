<template>
  <div class="calendar-page-container">
    <header class="view-header">
      <h1>Meu Calendário de Tarefas</h1>
    </header>

    <div class="calendar-wrapper card">
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
const tarefaSelecionada = ref<any>(null);
const tarefaParaEditar = ref<any>(null);

// --- MÉTODOS ---
const fetchTarefasApi = async (fetchInfo: any, successCallback: any, failureCallback: any) => {
  try {
    const response = await apiClient.get('/v1/minhas-tarefas/', {
      params: {
        start: fetchInfo.startStr,
        end: fetchInfo.endStr
      }
    });

    const events = response.data.map((tarefa: any) => ({
      id: tarefa.id,
      title: tarefa.titulo,
      start: tarefa.data_vencimento,
      allDay: false,
      extendedProps: {
        ...tarefa
      },
      classNames: [tarefa.concluida ? 'tarefa-concluida' : 'tarefa-pendente']
    }));
    successCallback(events);
  } catch (error) {
    console.error("Erro ao buscar tarefas:", error);
    failureCallback(error);
  }
};

const handleEventClick = (info: any) => {
  tarefaSelecionada.value = info.event.extendedProps;
  isDetalhesModalVisible.value = true;
};

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

// NOVO: Manipulador para cliques na data
const handleDateClick = (info: any) => {
  // Prepara uma nova tarefa com a data selecionada
  const dataInicial = info.dateStr;
  tarefaParaEditar.value = {
    data_vencimento: dataInicial
  };
  isEditModalVisible.value = true;
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
  dateClick: handleDateClick, // Adiciona o novo manipulador
});
</script>

<style scoped>
/* Estilos gerais da página */
.calendar-page-container {
  max-width: none;
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #333;
}

.view-header {
  margin-bottom: 0;
  border-bottom: none;
  padding: 0;
  display: none;
}

/* Estilo do cartão principal para o calendário */
.calendar-wrapper.card {
  background-color: #ffffff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e0e0;
  margin: 1rem;
}

/* Estilos de sobreposição para o FullCalendar */
:deep(.fc-toolbar-title) {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

:deep(.fc-toolbar-chunk) {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Estilo dos botões da barra de ferramentas */
:deep(.fc-button) {
  background-color: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #333;
  padding: 6px 12px;
  font-size: 0.8rem;
  border-radius: 20px;
  text-transform: capitalize;
  transition: all 0.2s ease;
  box-shadow: none;
}

:deep(.fc-button:hover) {
  background-color: #e2e8f0;
  color: #1a1a1a;
}

:deep(.fc-button-primary:not(:disabled).fc-button-active) {
  background-color: #007bff;
  border-color: #007bff;
  color: white;
  box-shadow: none;
}

:deep(.fc-button-primary:not(:disabled).fc-button-active:hover) {
  background-color: #0056b3;
  border-color: #0056b3;
}

/* Estilo dos dias do calendário */
:deep(.fc-daygrid-day-number) {
  font-weight: 600;
  font-size: 1rem;
  color: #1a1a1a;
  padding: 8px;
}

:deep(.fc-day-other .fc-daygrid-day-number) {
  color: #999;
}

/* Estilo dos eventos */
:deep(.fc-event) {
  border-radius: 4px;
  font-size: 0.8rem;
  padding: 2px 4px;
  cursor: pointer;
  border: none !important;
  font-weight: 500;
}

:deep(.fc-event-title) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tarefa-pendente {
  background-color: #e0f2ff;
  color: #007bff;
  border-left: 3px solid #007bff;
}

.tarefa-concluida {
  background-color: #e2e8f0;
  color: #6c757d;
  border-left: 3px solid #6c757d;
  opacity: 0.8;
}

/* Responsividade */
@media (max-width: 768px) {
  .calendar-page-container {
    padding: 1rem;
  }

  .calendar-wrapper.card {
    margin: 0.5rem;
  }

  .view-header h1 {
    font-size: 1.5rem;
  }
  
  :deep(.fc-toolbar-title) {
    font-size: 1.2rem;
  }

  :deep(.fc-toolbar.fc-header-toolbar) {
    flex-direction: column;
    align-items: flex-start;
  }

  :deep(.fc-toolbar.fc-header-toolbar > *) {
    margin-bottom: 1rem;
  }
}
</style>
<template>
  <div class="calendar-container">
    <FullCalendar :options="calendarOptions" ref="fullCalendar" />
    
    <TarefaModal
      v-if="modal.visible"
      :tarefa="modal.tarefa"
      :oportunidade-id="modal.oportunidadeId"
      :data-inicial="modal.dataInicial"
      @close="fecharModal"
      @saved="recarregarTarefas"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import TarefaModal from '@/components/TarefaModal.vue';

interface Tarefa {
  id: number;
  descricao: string;
  data_conclusao: string;
  concluida: boolean;
  oportunidade: number | null;
  oportunidade_titulo: string;
  cliente_nome: string;
  responsavel_nome: string;
  status_display: string;
}

const fullCalendar = ref<any>(null); // Referência para o componente FullCalendar

const modal = ref({
  visible: false,
  tarefa: null as any,
  dataInicial: '',
  oportunidadeId: null as any,
});

const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay'
  },
  locale: 'pt-br',
  editable: true,
  selectable: true,
  select: handleDateSelect,
  // CORREÇÃO: A URL para buscar as tarefas foi atualizada.
  events: async function(fetchInfo: any, successCallback: any, failureCallback: any) {
    try {
      const response = await apiClient.get('/v1/minhas-tarefas/', { // URL CORRIGIDA
        params: {
          start: fetchInfo.startStr,
          end: fetchInfo.endStr
        }
      });
      successCallback(response.data.map((tarefa: Tarefa) => ({
        id: tarefa.id,
        title: tarefa.oportunidade_titulo || tarefa.descricao,
        start: tarefa.data_conclusao,
        extendedProps: {
            status: tarefa.status_display,
            descricao: tarefa.descricao,
            responsavelNome: tarefa.responsavel_nome,
            oportunidadeId: tarefa.oportunidade,
            clienteNome: tarefa.cliente_nome, // Passando o nome do cliente
        },
        backgroundColor: getTaskColor(tarefa.status_display),
        borderColor: getTaskColor(tarefa.status_display),
        editable: !tarefa.concluida
      })));
    } catch (error) {
      console.error("Erro ao carregar tarefas:", error);
      failureCallback(error);
    }
  },
  eventClick: handleEventClick,
  eventChange: handleEventChange,
});

function handleDateSelect(selectInfo: any) {
  modal.value.dataInicial = selectInfo.startStr.split('T')[0];
  modal.value.oportunidadeId = null;
  modal.value.tarefa = null;
  modal.value.visible = true;
}

function handleEventClick(clickInfo: any) {
  modal.value.tarefa = {
    id: clickInfo.event.id,
    descricao: clickInfo.event.extendedProps.descricao,
    data_conclusao: clickInfo.event.startStr.split('T')[0],
    oportunidade: clickInfo.event.extendedProps.oportunidadeId,
    oportunidade_titulo: clickInfo.event.title,
    cliente_nome: clickInfo.event.extendedProps.clienteNome,
  };
  modal.value.oportunidadeId = clickInfo.event.extendedProps.oportunidadeId;
  modal.value.visible = true;
}

function fecharModal() {
  modal.value.visible = false;
  modal.value.tarefa = null;
  modal.value.dataInicial = '';
  modal.value.oportunidadeId = null;
}

async function recarregarTarefas() {
  fecharModal();
  // CORREÇÃO: Maneira mais simples e eficiente de recarregar os eventos do calendário.
  if (fullCalendar.value) {
    const calendarApi = fullCalendar.value.getApi();
    calendarApi.refetchEvents();
  }
}

async function handleEventChange(changeInfo: any) {
  const updatedTarefa = {
    data_conclusao: changeInfo.event.startStr, // Envia a data completa para o backend
  };
  const tarefaId = changeInfo.event.id;

  try {
    // CORREÇÃO: A URL de atualização é sempre a mesma, independentemente da oportunidade.
    await apiClient.patch(`/v1/tarefas/${tarefaId}/`, updatedTarefa);
  } catch (error) {
    console.error("Erro ao atualizar a tarefa:", error);
    changeInfo.revert();
  }
}

function getTaskColor(status: string) {
    switch (status) {
        case 'Concluída':
            return '#28a745';
        case 'Pendente':
            return '#ffc107';
        case 'Atrasada':
            return '#dc3545';
        default:
            return '#007bff';
    }
}

onMounted(() => {
  // O FullCalendar se encarrega de chamar a função 'events' no carregamento
});
</script>

<style scoped>
.calendar-container {
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* Estilos para customizar o FullCalendar se necessário */
:deep(.fc-button-primary) {
    background-color: #007bff;
    border-color: #007bff;
}
</style>
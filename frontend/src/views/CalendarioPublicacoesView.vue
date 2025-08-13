<template>
  <div class="calendario-container">
    <header class="view-header">
      <h1>Calendário de Publicações</h1>
      <p>Visualize as suas publicações agendadas, concluídas e as que falharam.</p>
    </header>

    <div class="card">
      <div class="card-body">
        <FullCalendar :options="calendarOptions" />
      </div>
    </div>
  </div>

  <div v-if="selectedEvent" class="modal-overlay" @click.self="selectedEvent = null">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Detalhes da Publicação</h3>
        <button @click="selectedEvent = null" class="close-button">&times;</button>
      </div>
      <div class="modal-body">
        <h4>{{ selectedEvent.title }}</h4>
        <p><strong>Status:</strong> <span :class="['status-badge', getStatusClass(selectedEvent.extendedProps.status)]">{{ formatStatus(selectedEvent.extendedProps.status) }}</span></p>
        <p><strong>Agendado para:</strong> {{ new Date(selectedEvent.start).toLocaleString('pt-BR') }}</p>
        
        <div class="texto-publicacao">
          <strong>Texto:</strong>
          <pre>{{ selectedEvent.extendedProps.texto }}</pre>
        </div>
        
        <div v-if="selectedEvent.extendedProps.status === 'ERRO'" class="resultado-erro">
          <strong>Motivo do Erro:</strong>
          <pre>{{ JSON.stringify(selectedEvent.extendedProps.resultado_publicacao, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import apiClient from '@/services/api';

const selectedEvent = ref<any | null>(null);

// Opções de configuração do FullCalendar
const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,dayGridWeek'
  },
  locale: 'pt-br',
  buttonText: {
      today:    'Hoje',
      month:    'Mês',
      week:     'Semana',
  },
  events: async (fetchInfo: any, successCallback: any, failureCallback: any) => {
    try {
      const response = await apiClient.get('/v1/publicacoes/calendario/', {
        params: {
          start: fetchInfo.startStr,
          end: fetchInfo.endStr,
        },
      });
      // Mapeia os eventos para adicionar cores com base no status
      const events = response.data.map((event: any) => ({
        ...event,
        backgroundColor: getEventColor(event.status),
        borderColor: getEventColor(event.status),
      }));
      successCallback(events);
    } catch (error) {
      console.error("Erro ao carregar eventos do calendário:", error);
      failureCallback(error);
    }
  },
  eventClick: (clickInfo: any) => {
    selectedEvent.value = clickInfo.event;
  }
});

function getEventColor(status: string): string {
  switch (status) {
    case 'PUBLICADO':
      return '#28a745'; // Verde
    case 'AGENDADO':
      return '#007bff'; // Azul
    case 'ERRO':
      return '#dc3545'; // Vermelho
    default:
      return '#6c757d'; // Cinza
  }
}

function getStatusClass(status: string): string {
  if (!status) return 'status-inativo';
  switch (status) {
      case 'PUBLICADO': return 'status-concluido';
      case 'AGENDADO': return 'status-pendente';
      case 'ERRO': return 'status-erro';
      default: return 'status-inativo';
  }
}

function formatStatus(status: string): string {
    return status ? status.replace(/_/g, ' ') : 'N/A';
}
</script>

<style scoped>
.calendario-container {
  padding: 2rem;
}
.card {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Estilos para o Modal de Detalhes */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-container { background-color: white; border-radius: 8px; width: 90%; max-width: 600px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
.modal-header { padding: 1rem 1.5rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.close-button { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #aaa; }
.modal-body { padding: 1.5rem; }
.modal-body h4 { margin-top: 0; }
.texto-publicacao, .resultado-erro { margin-top: 1rem; padding: 0.8rem; background-color: #f8f9fa; border-radius: 4px; }
pre { white-space: pre-wrap; word-wrap: break-word; font-family: inherit; margin: 0; }
.resultado-erro { background-color: #f8d7da; color: #721c24; }

/* Badges de Status */
.status-badge { padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; color: white; }
.status-concluido { background-color: #28a745; }
.status-pendente { background-color: #007bff; }
.status-erro { background-color: #dc3545; }
.status-inativo { background-color: #6c757d; }
</style>
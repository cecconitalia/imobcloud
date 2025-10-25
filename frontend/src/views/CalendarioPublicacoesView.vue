<template>
  <div class="calendario-container">
    <header class="view-header">
      <h1>Calendário de Publicações</h1>
      <p>Visualize e gira as suas publicações agendadas, concluídas e as que falharam.</p>
    </header>

    <div class="card">
      <div class="card-body">
        <FullCalendar :options="calendarOptions" ref="calendar" />
      </div>
    </div>
  </div>

  <div v-if="selectedEvent" class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Editar Agendamento</h3>
        <button @click="closeModal" class="close-button">&times;</button>
      </div>
      <div class="modal-body">
        <h4>{{ selectedEvent.title }}</h4>
        
        <div class="form-group">
          <label for="event-text">Texto da Publicação:</label>
          <textarea id="event-text" v-model="editableEvent.texto" rows="8"></textarea>
        </div>

        <div class="form-group">
          <label for="event-date">Data do Agendamento:</label>
          <input type="datetime-local" id="event-date" v-model="editableEvent.data_agendamento">
        </div>
        
        <div class="form-group">
          <label>Plataformas:</label>
          <div class="plataformas-edit">
            <label><input type="checkbox" value="facebook" v-model="editableEvent.plataformas"> Facebook</label>
            <label><input type="checkbox" value="instagram" v-model="editableEvent.plataformas"> Instagram</label>
          </div>
        </div>

        <div v-if="selectedEvent.extendedProps.status === 'ERRO'" class="resultado-erro">
          <strong>Motivo do Erro:</strong>
          <pre>{{ JSON.stringify(selectedEvent.extendedProps.resultado_publicacao, null, 2) }}</pre>
        </div>
      </div>
      <div class="modal-footer">
        <button @click="handleDelete" class="btn-danger" :disabled="isSaving || isDeleting">
            {{ isDeleting ? 'A Excluir...' : 'Excluir Agendamento' }}
        </button>
        <button @click="handleSave" class="btn-primary" :disabled="isSaving || isDeleting">
            {{ isSaving ? 'A Salvar...' : 'Salvar Alterações' }}
        </button>
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
import { EventClickArg } from '@fullcalendar/core';

const selectedEvent = ref<any | null>(null);
const editableEvent = ref<any>({});
const calendar = ref<any | null>(null); // Referência para o componente FullCalendar
const isSaving = ref(false);
const isDeleting = ref(false);

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
  eventClick: (clickInfo: EventClickArg) => {
    selectedEvent.value = clickInfo.event;
    // Formata a data para o formato 'YYYY-MM-DDTHH:mm' que o input datetime-local espera
    const localDateTime = new Date(clickInfo.event.start.getTime() - (clickInfo.event.start.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
    editableEvent.value = {
        id: clickInfo.event.id,
        texto: clickInfo.event.extendedProps.texto,
        plataformas: [...clickInfo.event.extendedProps.plataformas],
        data_agendamento: localDateTime,
    };
  }
});

function getEventColor(status: string): string {
  switch (status) {
    case 'PUBLICADO': return '#28a745';
    case 'AGENDADO': return '#007bff';
    case 'ERRO': return '#dc3545';
    default: return '#6c757d';
  }
}

async function handleSave() {
    if (!editableEvent.value.id) return;
    isSaving.value = true;
    try {
        await apiClient.put(`/v1/publicacoes/posts-agendados/${editableEvent.value.id}/`, {
            texto: editableEvent.value.texto,
            data_agendamento: new Date(editableEvent.value.data_agendamento).toISOString(),
            plataformas: editableEvent.value.plataformas
        });
        closeModal();
        calendar.value.getApi().refetchEvents(); // Recarrega os eventos no calendário
    } catch (error) {
        console.error("Erro ao salvar o agendamento:", error);
        alert("Não foi possível salvar as alterações.");
    } finally {
        isSaving.value = false;
    }
}

async function handleDelete() {
    if (!editableEvent.value.id) return;
    if (!window.confirm("Tem a certeza de que deseja excluir este agendamento? Esta ação não pode ser desfeita.")) {
        return;
    }
    isDeleting.value = true;
    try {
        await apiClient.delete(`/v1/publicacoes/posts-agendados/${editableEvent.value.id}/`);
        closeModal();
        calendar.value.getApi().refetchEvents(); // Recarrega os eventos no calendário
    } catch (error) {
        console.error("Erro ao excluir o agendamento:", error);
        alert("Não foi possível excluir o agendamento.");
    } finally {
        isDeleting.value = false;
    }
}

function closeModal() {
    selectedEvent.value = null;
    editableEvent.value = {};
}
</script>

<style scoped>
.calendario-container { padding: 2rem; }
.card { background-color: #fff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

/* Estilos do Modal */
.modal-overlay { /* ... */ }
.modal-container { /* ... */ }
.modal-header { /* ... */ }
.modal-body { 
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
.form-group label {
    display: block;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.form-group textarea, .form-group input {
    width: 100%;
    padding: 0.75rem;
    border-radius: 4px;
    border: 1px solid #ccc;
}
.plataformas-edit {
    display: flex;
    gap: 1rem;
}
.modal-footer {
    padding: 1rem 1.5rem;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
}
.btn-danger {
    background-color: #dc3545;
    color: white;
}
.btn-primary {
    background-color: #007bff;
    color: white;
}
.btn-danger:disabled, .btn-primary:disabled {
    background-color: #6c757d;
    cursor: not-allowed;
}
/* ... (outros estilos) ... */
</style>
<template>
  <div class="calendario-container">
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
// CORREÇÃO AQUI: Adicionado 'type' para importar apenas a definição de tipo
import type { EventClickArg } from '@fullcalendar/core';

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
    const localDateTime = new Date(clickInfo.event.start!.getTime() - (clickInfo.event.start!.getTimezoneOffset() * 60000)).toISOString().slice(0, 16);
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
        // Verifica se calendar.value.getApi existe antes de chamar refetchEvents
        if (calendar.value && calendar.value.getApi) {
             calendar.value.getApi().refetchEvents(); // Recarrega os eventos no calendário
        }
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
         // Verifica se calendar.value.getApi existe antes de chamar refetchEvents
        if (calendar.value && calendar.value.getApi) {
             calendar.value.getApi().refetchEvents(); // Recarrega os eventos no calendário
        }
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
.calendario-container {
  padding: 0; 
}

.card {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.card-body {
    padding: 0;
}

/* Estilos do Modal */
.modal-overlay {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0, 0, 0, 0.6); display: flex; justify-content: center;
    align-items: center; z-index: 1050;
}
.modal-container {
    background: #fff; padding: 0; border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    width: 90%; max-width: 600px;
}
.modal-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 1rem 1.5rem; border-bottom: 1px solid #eee;
}
.modal-header h3 { margin: 0; font-size: 1.2rem; }
.close-button {
    background: none; border: none; font-size: 1.5rem; cursor: pointer;
    color: #6c757d; line-height: 1;
}
.modal-body {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
.form-group label {
    display: block; font-weight: 600; margin-bottom: 0.5rem;
}
.form-group textarea, .form-group input {
    width: 100%; padding: 0.75rem; border-radius: 4px; border: 1px solid #ccc;
    box-sizing: border-box;
}
.plataformas-edit { display: flex; gap: 1rem; }
.resultado-erro {
    background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;
    padding: 1rem; border-radius: 4px;
}
.resultado-erro pre {
    margin: 0.5rem 0 0 0; white-space: pre-wrap; font-size: 0.8rem;
}

.modal-footer {
    padding: 1rem 1.5rem; border-top: 1px solid #eee;
    display: flex; justify-content: flex-end; gap: 1rem;
}
.btn-danger, .btn-primary {
    padding: 10px 15px; border-radius: 4px; font-weight: 500; border: none;
    cursor: pointer; transition: background-color 0.2s;
}
.btn-danger { background-color: #dc3545; color: white; }
.btn-primary { background-color: #007bff; color: white; }
.btn-danger:hover { background-color: #c82333; }
.btn-primary:hover { background-color: #0056b3; }
.btn-danger:disabled, .btn-primary:disabled {
    background-color: #adb5bd; cursor: not-allowed;
}
</style>
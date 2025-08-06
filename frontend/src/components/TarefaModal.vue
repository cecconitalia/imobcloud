<template>
  <div class="modal-overlay">
    <div class="modal-container">
      <div class="modal-header">
        <h3>{{ isEditing ? 'Editar Tarefa' : 'Adicionar Nova Tarefa' }}</h3>
        <button @click="emit('close')" class="close-btn">&times;</button>
      </div>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="descricao">Descrição</label>
          <textarea id="descricao" v-model="tarefaLocal.descricao" required></textarea>
        </div>
        <div class="form-group">
          <label for="data_conclusao">Prazo</label>
          <input type="date" id="data_conclusao" v-model="tarefaLocal.data_conclusao" />
        </div>
        <div class="modal-actions">
          <button v-if="isEditing" type="button" @click="handleDelete" class="btn-danger">
            Eliminar
          </button>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'A guardar...' : 'Guardar' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, onMounted } from 'vue';
import apiClient from '@/services/api';

const props = defineProps({
  oportunidadeId: { type: [String, Number], required: true },
  tarefa: { type: Object, default: null },
});

const emit = defineEmits(['close', 'saved']);

const isEditing = ref(false);
const isSubmitting = ref(false);
const tarefaLocal = ref({
  id: null,
  descricao: '',
  data_conclusao: '',
  oportunidade: props.oportunidadeId,
});

onMounted(() => {
  if (props.tarefa) {
    isEditing.value = true;
    tarefaLocal.value = { ...props.tarefa };
  }
});

async function handleSubmit() {
  isSubmitting.value = true;
  try {
    if (isEditing.value) {
      await apiClient.patch(`/v1/clientes/oportunidades/${props.oportunidadeId}/tarefas/${tarefaLocal.value.id}/`, tarefaLocal.value);
    } else {
      await apiClient.post(`/v1/clientes/oportunidades/${props.oportunidadeId}/tarefas/`, tarefaLocal.value);
    }
    emit('saved');
  } catch (error) {
    console.error("Erro ao salvar a tarefa:", error);
    alert('Ocorreu um erro ao salvar a tarefa.');
  } finally {
    isSubmitting.value = false;
  }
}

async function handleDelete() {
  if (!window.confirm('Tem certeza que deseja eliminar esta tarefa?')) {
    return;
  }
  isSubmitting.value = true;
  try {
    await apiClient.delete(`/v1/clientes/oportunidades/${props.oportunidadeId}/tarefas/${tarefaLocal.value.id}/`);
    emit('saved');
  } catch (error) {
    console.error("Erro ao eliminar a tarefa:", error);
    alert('Ocorreu um erro ao eliminar a tarefa.');
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.modal-header h3 {
  margin: 0;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}
.form-group {
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: column;
}
.form-group label {
    font-weight: bold;
    margin-bottom: 0.5rem;
}
.form-group textarea,
.form-group input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
    box-sizing: border-box;
}
.modal-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
.btn-primary, .btn-danger {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}
.btn-primary { background-color: #007bff; color: white; }
.btn-danger { background-color: #dc3545; color: white; }
</style>
<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Detalhes da Tarefa</h3>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>

      <div v-if="tarefa">
        <p><strong>Título:</strong> {{ tarefa.title }}</p>
        <p><strong>Prazo:</strong> {{ formatarData(tarefa.start) }}</p>
        <p><strong>Status:</strong> <span :style="{ color: tarefa.backgroundColor }">{{ tarefa.extendedProps.status }}</span></p>
        <p><strong>Responsável:</strong> {{ tarefa.extendedProps.responsavelNome }}</p>
        <p v-if="tarefa.extendedProps.descricao"><strong>Descrição:</strong> {{ tarefa.extendedProps.descricao }}</p>
        </div>

      <div class="modal-actions">
        <button @click="closeModal" class="btn-secondary">Fechar</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  tarefa: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(['close']);

function closeModal() {
  emit('close');
}

function formatarData(data: string) {
  const dataObj = new Date(data);
  return dataObj.toLocaleDateString('pt-BR');
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

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  line-height: 1;
}

.modal-actions {
  margin-top: 1.5rem;
  text-align: right;
}

.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  background-color: #6c757d;
  color: white;
}
</style>
<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Histórico de Publicações</h2>
        <button @click="$emit('close')" class="close-button">&times;</button>
      </div>
      <div v-if="isLoading" class="modal-loading-message">
        <div class="spinner"></div>
        <p>A carregar histórico...</p>
      </div>
      <div v-else-if="historico.length > 0" class="modal-body">
        <ul class="history-list">
          <li v-for="item in historico" :key="item.id" class="history-item">
            <div class="history-item-details">
              <strong>Rede Social:</strong> {{ item.rede_social }}
              <br>
              <strong>Data:</strong> {{ formatDate(item.data_publicacao) }}
            </div>
          </li>
        </ul>
      </div>
      <div v-else class="modal-body no-history-message">
        <p>Nenhuma publicação encontrada para este imóvel.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';
import '@fortawesome/fontawesome-free/css/all.css';

const props = defineProps({
  imovelId: {
    type: Number,
    required: true,
  },
});

const emits = defineEmits(['close']);

const historico = ref<any[]>([]);
const isLoading = ref(true);

async function fetchHistorico() {
  isLoading.value = true;
  try {
    // --- CORREÇÃO AQUI: URL ajustada para incluir o prefixo 'publicacoes' ---
    const response = await apiClient.get(`/v1/publicacoes/imoveis/${props.imovelId}/historico/`);
    historico.value = response.data;
  } catch (error) {
    console.error("Erro ao buscar histórico de publicações:", error);
    historico.value = [];
  } finally {
    isLoading.value = false;
  }
}

function formatDate(dateString: string) {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  };
  return new Date(dateString).toLocaleDateString('pt-BR', options);
}

onMounted(() => {
  fetchHistorico();
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 600px;
  position: relative;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #343a40;
}
.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #6c757d;
}
.modal-body {
  max-height: 70vh;
  overflow-y: auto;
}
.modal-loading-message, .no-history-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}
.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.history-item {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 0.75rem;
}
.history-item-details {
  font-size: 1em;
  color: #495057;
}
.history-link {
  color: #007bff;
  text-decoration: none;
  font-weight: 600;
  margin-top: 0.5rem;
  display: inline-block;
}
.history-link:hover {
  text-decoration: underline;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
<template>
  <div v-if="show" class="modal-backdrop" @click="closeModal">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h3>Histórico de Publicações</h3>
        <button @click="closeModal">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="loading">Carregando histórico...</div>
        <div v-else-if="error">{{ error }}</div>
        <ul v-else-if="historico.length > 0">
          <li v-for="item in historico" :key="item.id">
            <p><strong>Data:</strong> {{ new Date(item.data_publicacao).toLocaleString('pt-BR') }}</p>
            <p><strong>Status:</strong> <span :class="`status-${item.status.toLowerCase()}`">{{ item.status }}</span></p>
            <p><strong>Rede Social:</strong> {{ item.rede_social }}</p>
            <p><strong>Resposta da API:</strong> <code>{{ item.api_response }}</code></p>
          </li>
        </ul>
        <div v-else>Nenhum histórico encontrado para este imóvel.</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import apiClient from '@/services/api';

const props = defineProps<{
  show: boolean;
  imovelId: number | null;
}>();

const emit = defineEmits(['close']);

const historico = ref<any[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);

const fetchHistorico = async (id: number) => {
  loading.value = true;
  error.value = null;
  try {
    const response = await apiClient.get(`/publicacoes/historico/imovel/${id}/`);
    historico.value = response.data;
  } catch (err) {
    error.value = 'Falha ao carregar o histórico.';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

watch(() => props.imovelId, (newId) => {
  if (newId) {
    fetchHistorico(newId);
  } else {
    historico.value = [];
  }
});

const closeModal = () => {
  emit('close');
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}
.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
.modal-body {
  padding: 1rem;
  overflow-y: auto;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  border-bottom: 1px solid #eee;
  padding: 1rem 0;
}
li:last-child {
  border-bottom: none;
}
p {
  margin: 0.25rem 0;
}
.status-sucesso {
  color: green;
  font-weight: bold;
}
.status-falha {
  color: red;
  font-weight: bold;
}
</style>
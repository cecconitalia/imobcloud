<template>
  <div class="atividades-container">
    <h3 class="timeline-title">Histórico de Atividades</h3>

    <div class="nova-atividade-form">
      <textarea
        v-model="novaNota"
        placeholder="Adicionar uma nova nota sobre este cliente..."
        rows="3"
      ></textarea>
      <button @click="adicionarNota" :disabled="isSubmittingNota">
        {{ isSubmittingNota ? 'A Guardar...' : 'Guardar Nota' }}
      </button>
    </div>

    <div v-if="isLoading" class="loading-message">A carregar histórico...</div>
    <div v-else-if="atividades.length === 0" class="no-data-message">
      Nenhuma atividade registada para este cliente.
    </div>
    <ul v-else class="timeline">
      <li v-for="atividade in atividades" :key="atividade.id" class="timeline-item">
        <div class="timeline-icon" :class="getIconClass(atividade.tipo)"></div>
        <div class="timeline-content">
          <p class="atividade-descricao">{{ atividade.descricao }}</p>
          <small class="atividade-meta">
            <strong>{{ atividade.registrado_por_obj?.first_name || 'Sistema' }} ({{ atividade.registrado_por_obj?.username || 'N/A' }})</strong> em {{ formatarData(atividade.data_criacao) }}
          </small>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps } from 'vue';
import apiClient from '@/services/api';

const props = defineProps<{
  clienteId: string | number;
}>();

const atividades = ref<any[]>([]);
const isLoading = ref(true);
const novaNota = ref('');
const isSubmittingNota = ref(false);

async function fetchAtividades() {
  isLoading.value = true;
  try {
    const response = await apiClient.get('/v1/atividades/', {
      params: { cliente_id: props.clienteId }
    });
    atividades.value = response.data;
  } catch (error) {
    console.error("Erro ao carregar atividades:", error);
  } finally {
    isLoading.value = false;
  }
}

async function adicionarNota() {
  if (!novaNota.value.trim()) return;

  isSubmittingNota.value = true;
  try {
    const payload = {
      cliente: props.clienteId,
      tipo: 'NOTA',
      descricao: novaNota.value,
    };
    await apiClient.post('/v1/atividades/', payload);
    novaNota.value = '';
    await fetchAtividades(); // Recarrega a lista
  } catch (error) {
    console.error("Erro ao adicionar nota:", error);
    alert('Não foi possível guardar a nota.');
  } finally {
    isSubmittingNota.value = false;
  }
}

onMounted(() => {
  fetchAtividades();
});

function formatarData(data: string): string {
  if (!data) return '';
  return new Date(data).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

function getIconClass(tipo: string): string {
  switch (tipo.toUpperCase()) {
    case 'LIGACAO': return 'fas fa-phone-alt';
    case 'EMAIL': return 'fas fa-envelope';
    case 'WHATSAPP': return 'fab fa-whatsapp';
    case 'NOTA': return 'fas fa-sticky-note';
    case 'MUDANCA_FASE': return 'fas fa-exchange-alt';
    default: return 'fas fa-info-circle';
  }
}
</script>

<style scoped>
.atividades-container {
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
}
.timeline-title {
  margin-bottom: 1.5rem;
}

.nova-atividade-form {
  margin-bottom: 2rem;
}
.nova-atividade-form textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  margin-bottom: 0.5rem;
  box-sizing: border-box;
}
.nova-atividade-form button {
  background-color: #28a745;
  color: white;
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.nova-atividade-form button:disabled {
  background-color: #a3d9b1;
}

.timeline {
  list-style: none;
  padding: 0;
}
.timeline-item {
  display: flex;
  margin-bottom: 1.5rem;
}
.timeline-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  flex-shrink: 0;
}
.timeline-content {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 5px;
  flex-grow: 1;
}
.atividade-descricao {
  margin-top: 0;
  margin-bottom: 0.5rem;
}
.atividade-meta {
  font-size: 0.8em;
  color: #6c757d;
}
</style>
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
            <strong>{{ atividade.registrado_por_obj?.username || 'Sistema' }}</strong> em {{ formatarData(atividade.data_criacao) }}
          </small>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps } from 'vue';
import apiClient from '@/services/api';

// Este componente recebe o ID do cliente como uma "propriedade"
const props = defineProps({
  clienteId: {
    type: [String, Number],
    required: true
  }
});

const atividades = ref<any[]>([]);
const isLoading = ref(true);
const novaNota = ref('');
const isSubmittingNota = ref(false);

// Função para buscar as atividades do cliente na API
async function fetchAtividades() {
  isLoading.value = true;
  try {
    const response = await apiClient.get(`/v1/clientes/clientes/${props.clienteId}/atividades/`);
    atividades.value = response.data;
  } catch (error) {
    console.error("Erro ao buscar atividades:", error);
  } finally {
    isLoading.value = false;
  }
}

// Função para adicionar uma nova nota
async function adicionarNota() {
  if (!novaNota.value.trim()) return;

  isSubmittingNota.value = true;
  try {
    const novaAtividade = {
      cliente: props.clienteId,
      tipo: 'NOTA',
      descricao: novaNota.value,
    };
    // Faz o POST para o endpoint geral de atividades
    await apiClient.post('/v1/clientes/atividades/', novaAtividade);
    novaNota.value = ''; // Limpa o campo
    await fetchAtividades(); // Recarrega a lista para mostrar a nova nota
  } catch (error) {
    console.error("Erro ao adicionar nota:", error);
    alert('Não foi possível adicionar a nota.');
  } finally {
    isSubmittingNota.value = false;
  }
}

// Executa a busca de atividades assim que o componente é montado
onMounted(() => {
  fetchAtividades();
});

// Funções de ajuda para formatação
function formatarData(data: string) {
  return new Date(data).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

function getIconClass(tipo: string): string {
  // Retorna uma classe CSS para o ícone com base no tipo de atividade
  // (Poderíamos adicionar ícones reais para cada tipo no futuro)
  return `icon-${tipo.toLowerCase()}`;
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
  background-color: #e0e0e0;
  margin-right: 1rem;
  flex-shrink: 0;
  /* Simples "ícones" com cores diferentes */
}
.icon-nota { background-color: #ffc107; }
.icon-visita { background-color: #17a2b8; }
.icon-contrato { background-color: #28a745; }

.timeline-content {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 5px;
  width: 100%;
}
.atividade-descricao {
  margin: 0 0 0.5rem 0;
  white-space: pre-wrap; /* Preserva as quebras de linha da nota */
}
.atividade-meta {
  color: #6c757d;
  font-size: 0.85em;
}
</style>
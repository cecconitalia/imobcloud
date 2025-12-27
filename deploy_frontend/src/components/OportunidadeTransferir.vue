<template>
  <div class="transfer-container">
    <h4 class="transfer-title">Transferir Oportunidade</h4>
    <div class="transfer-form">
      <div v-if="isLoadingCorretores">A carregar corretores...</div>
      <div v-else class="form-group">
        <label for="novoCorretor">Selecionar novo corretor</label>
        <select id="novoCorretor" v-model="novoCorretorId" class="corretor-select">
          <option :value="null">Nenhum</option>
          <option v-for="corretor in corretores" :key="corretor.id" :value="corretor.id">
            {{ corretor.first_name || corretor.username }}
          </option>
        </select>
      </div>
      <button
        @click="transferir"
        :disabled="isTransferring || !novoCorretorId"
        class="btn-transferir"
      >
        {{ isTransferring ? 'A transferir...' : 'Transferir' }}
      </button>
    </div>
    <div v-if="transferMessage" :class="messageClass">{{ transferMessage }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, defineProps, defineEmits } from 'vue';
import apiClient from '@/services/api';

const props = defineProps({
  oportunidadeId: {
    type: String,
    required: true
  },
  corretorResponsavelId: {
    type: [Number, String, null],
    required: true
  }
});

const emit = defineEmits(['transferido']);

const corretores = ref<any[]>([]);
const isLoadingCorretores = ref(true);
const isTransferring = ref(false);
const novoCorretorId = ref<number | null>(null);
const transferMessage = ref('');
const messageClass = ref('');

// This computed property filters out the current owner from the transfer list
const corretoresDisponiveis = computed(() => {
  return corretores.value.filter(c => c.id !== props.corretorResponsavelId);
});

async function fetchCorretores() {
  isLoadingCorretores.value = true;
  try {
    // **CORRECTION IS HERE: URL path is now correct.**
    const response = await apiClient.get('/v1/corretores/');
    corretores.value = response.data;
  } catch (error) {
    console.error("Erro ao carregar corretores:", error);
  } finally {
    isLoadingCorretores.value = false;
  }
}

async function transferir() {
  if (!novoCorretorId.value) return;

  if (!window.confirm('Tem a certeza que deseja transferir esta oportunidade?')) {
    return;
  }

  isTransferring.value = true;
  transferMessage.value = '';
  messageClass.value = '';

  try {
    // **CORRECTION IS HERE: Changed to PATCH and using the correct endpoint.**
    // We are partially updating the opportunity with the new responsible person's ID.
    await apiClient.patch(`/v1/oportunidades/${props.oportunidadeId}/`, {
      responsavel: novoCorretorId.value
    });
    transferMessage.value = 'Oportunidade transferida com sucesso!';
    messageClass.value = 'success-message';
    emit('transferido');
  } catch (error: any) {
    console.error("Erro ao transferir oportunidade:", error.response?.data || error);
    transferMessage.value = error.response?.data?.detail || 'Ocorreu um erro ao transferir.';
    messageClass.value = 'error-message';
  } finally {
    isTransferring.value = false;
  }
}

onMounted(() => {
  fetchCorretores();
});
</script>

<style scoped>
.transfer-container {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
}
.transfer-title {
  margin-bottom: 1rem;
}
.transfer-form {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  margin-bottom: 1rem;
}
.form-group {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}
.corretor-select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.btn-transferir {
  padding: 8px 16px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn-transferir:disabled {
  background-color: #a3d9b1;
  cursor: not-allowed;
}
.success-message {
  color: green;
  font-weight: bold;
}
.error-message {
  color: red;
  font-weight: bold;
}
</style>
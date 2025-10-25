<template>
  <div class="page-container">
    <div class="header-section">
      <h1 class="page-title">{{ formTitle }}</h1>
    </div>

    <div v-if="isLoading" class="loading-state">
      <p>A carregar...</p>
    </div>

    <div v-else class="form-card">
      <form @submit.prevent="submitForm">
        
        <div class="form-group">
          <label for="nome" class="form-label">Nome da Conta:</label>
          <input type="text" id="nome" v-model="conta.nome" class="form-input" required>
        </div>

        <div class="form-group">
          <label for="banco" class="form-label">Banco:</label>
          <input type="text" id="banco" v-model="conta.banco" class="form-input" required>
        </div>
        
        <div class="form-group">
          <label for="agencia" class="form-label">Agência:</label>
          <input type="text" id="agencia" v-model="conta.agencia" class="form-input" required>
        </div>

        <div class="form-group">
          <label for="numero_conta" class="form-label">Número da Conta:</label>
          <input type="text" id="numero_conta" v-model="conta.numero_conta" class="form-input" required>
        </div>

        <div class="form-group">
          <label for="saldo_inicial" class="form-label">Saldo Inicial:</label>
          <input type="number" id="saldo_inicial" v-model.number="conta.saldo_inicial" step="0.01" class="form-input" required>
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div class="actions">
          <button type="submit" class="submit-button">Salvar</button>
          <router-link :to="{ name: 'lista-contas' }" class="cancel-link">Cancelar</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';

interface Conta {
  id?: number;
  nome: string;
  banco: string;
  agencia: string;
  numero_conta: string;
  saldo_inicial: number;
}

const route = useRoute();
const router = useRouter();

const conta = ref<Conta>({
  nome: '',
  banco: '',
  agencia: '',
  numero_conta: '',
  saldo_inicial: 0,
});

const isLoading = ref(false);
const error = ref<string | null>(null);

const isEditing = computed(() => !!route.params.id);
const formTitle = computed(() => isEditing.value ? 'Editar Conta Bancária' : 'Adicionar Nova Conta Bancária');

const fetchConta = async (id: number) => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await api.get(`/v1/financeiro/contas/${id}/`);
    conta.value = response.data;
  } catch (err) {
    console.error('Erro ao buscar conta:', err);
    error.value = 'Falha ao carregar os dados da conta.';
  } finally {
    isLoading.value = false;
  }
};

const submitForm = async () => {
  try {
    if (isEditing.value) {
      await api.put(`/v1/financeiro/contas/${conta.value.id}/`, conta.value);
    } else {
      await api.post('/v1/financeiro/contas/', conta.value);
    }
    router.push({ name: 'lista-contas' });
  } catch (err: any) {
    console.error('Erro ao salvar conta:', err);
    if (err.response && err.response.data) {
        error.value = JSON.stringify(err.response.data);
    } else {
        error.value = 'Falha ao salvar a conta. Verifique os dados e tente novamente.';
    }
  }
};

onMounted(() => {
  if (isEditing.value) {
    fetchConta(Number(route.params.id));
  }
});
</script>

<style scoped>
.page-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.header-section {
  margin-bottom: 2rem;
  text-align: center;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
}

.form-card {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.loading-state {
  text-align: center;
  font-size: 1.2rem;
  color: #666;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #555;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #007bff;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.submit-button, .cancel-link {
  padding: 12px 24px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s, color 0.3s;
}

.submit-button {
  background-color: #007bff;
  color: white;
  border: none;
}

.submit-button:hover {
  background-color: #0056b3;
}

.cancel-link {
  background-color: #6c757d;
  color: white;
  border: none;
}

.cancel-link:hover {
  background-color: #5a6268;
}

.error-message {
  color: #d9534f;
  background-color: #f2dede;
  border: 1px solid #ebccd1;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
  margin-bottom: 1rem;
}
</style>
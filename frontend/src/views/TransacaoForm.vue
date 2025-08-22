<template>
  <div class="page-container">
    <header class="view-header">
      <h1>{{ isEditing ? 'Editar Transação' : 'Adicionar Nova Transação' }}</h1>
    </header>

    <div v-if="isLoading" class="loading-state">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <form v-if="!isLoading" @submit.prevent="submitForm" class="form-card">
      <div class="form-group">
        <label for="descricao">Descrição</label>
        <input type="text" id="descricao" v-model="transacao.descricao" required>
      </div>
      <div class="form-group">
        <label for="valor">Valor</label>
        <input type="number" step="0.01" id="valor" v-model="transacao.valor" required>
      </div>
      <div class="form-group">
        <label for="data_vencimento">Data de Vencimento</label>
        <input type="date" id="data_vencimento" v-model="transacao.data_vencimento" required>
      </div>
      <div class="form-group">
        <label for="tipo">Tipo</label>
        <select id="tipo" v-model="transacao.tipo" @change="fetchCategorias" required>
          <option value="RECEITA">Receita</option>
          <option value="DESPESA">Despesa</option>
        </select>
      </div>
      <div class="form-group">
        <label for="categoria">Categoria</label>
        <select id="categoria" v-model="transacao.categoria">
          <option :value="null">-- Nenhuma --</option>
          <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nome }}</option>
        </select>
      </div>
      <div class="form-actions">
        <button type="submit" class="btn-primary">Salvar</button>
        <router-link to="/financeiro/transacoes" class="btn-secondary">Cancelar</router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/services/api';

const route = useRoute();
const router = useRouter();
const isEditing = computed(() => !!route.params.id);

const transacao = ref<any>({
  descricao: '',
  valor: 0,
  data_vencimento: new Date().toISOString().split('T')[0],
  tipo: 'RECEITA',
  categoria: null,
});
const categorias = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

async function fetchCategorias() {
  if (!transacao.value.tipo) return;
  try {
    // CORREÇÃO: Removido o '/api' duplicado
    const response = await apiClient.get(`/v1/financeiro/categorias/?tipo=${transacao.value.tipo}`);
    categorias.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar categorias:", err);
  }
}

async function fetchTransacao(id: string) {
  try {
    // CORREÇÃO: Removido o '/api' duplicado
    const response = await apiClient.get(`/v1/financeiro/transacoes/${id}/`);
    // Garante que a data esteja no formato AAAA-MM-DD para o input
    response.data.data_vencimento = response.data.data_vencimento.split('T')[0];
    transacao.value = response.data;
    await fetchCategorias(); 
  } catch (err)
 {
    console.error("Erro ao buscar transação:", err);
    error.value = 'Falha ao carregar a transação.';
  }
}

async function submitForm() {
  try {
    // Garante que a data de transação exista ao salvar
    const payload = {
        ...transacao.value,
        data_transacao: transacao.value.data_transacao || new Date().toISOString().split('T')[0]
    };

    if (isEditing.value) {
      // CORREÇÃO: Removido o '/api' duplicado
      await apiClient.put(`/v1/financeiro/transacoes/${route.params.id}/`, payload);
    } else {
      // CORREÇÃO: Removido o '/api' duplicado
      await apiClient.post('/v1/financeiro/transacoes/', payload);
    }
    router.push('/financeiro/transacoes');
  } catch (err) {
    console.error("Erro ao salvar transação:", err);
    error.value = 'Falha ao salvar. Verifique os dados.';
  }
}

onMounted(async () => {
  if (isEditing.value) {
    await fetchTransacao(route.params.id as string);
  } else {
    await fetchCategorias();
  }
  isLoading.value = false;
});
</script>

<style scoped>
.page-container { padding: 2rem; max-width: 800px; margin: auto; }
.view-header h1 { margin-bottom: 2rem; }
.form-card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: .5rem; font-weight: bold; }
.form-group input, .form-group select { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.form-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2rem; }
.btn-primary { background-color: #007bff; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; }
.btn-secondary { background-color: #6c757d; color: white; text-decoration: none; padding: 12px 20px; border-radius: 5px; font-weight: bold; }
</style>
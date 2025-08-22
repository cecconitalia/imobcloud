<template>
  <div class="page-container">
    <header class="view-header">
      <h1>Transações Financeiras</h1>
      <router-link to="/financeiro/transacoes/nova" class="btn-primary">+ Adicionar Transação</router-link>
    </header>

    <div v-if="isLoading" class="loading-state">A carregar transações...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="transacoes.length" class="table-wrapper">
      <table class="styled-table">
        <thead>
          <tr>
            <th>Descrição</th>
            <th>Valor</th>
            <th>Data</th>
            <th>Vencimento</th>
            <th>Tipo</th>
            <th>Status</th>
            <th>Categoria</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="transacao in transacoes" :key="transacao.id">
            <td>{{ transacao.descricao }}</td>
            <td :class="transacao.tipo === 'RECEITA' ? 'text-success' : 'text-danger'">{{ formatarValor(transacao.valor) }}</td>
            <td>{{ formatarData(transacao.data_transacao) }}</td>
            <td>{{ formatarData(transacao.data_vencimento) }}</td>
            <td>{{ transacao.tipo }}</td>
            <td>{{ transacao.status }}</td>
            <td>{{ transacao.categoria?.nome || 'N/A' }}</td>
            <td>
              <router-link :to="`/financeiro/transacoes/editar/${transacao.id}`" class="btn-edit">Editar</router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else-if="!isLoading" class="no-data-message">
      Nenhuma transação encontrada.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const transacoes = ref<any[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);

function formatarValor(valor: number) {
  return parseFloat(valor.toString()).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formatarData(data: string) {
  if (!data) return '';
  return new Date(data + 'T00:00:00').toLocaleDateString('pt-BR');
}

async function fetchTransacoes() {
  isLoading.value = true;
  try {
    // CORREÇÃO: Removido o '/api' duplicado. A chamada começa com '/v1'.
    const response = await apiClient.get('/v1/financeiro/transacoes/');
    transacoes.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar transações:", err);
    error.value = 'Falha ao carregar as transações.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchTransacoes();
});
</script>

<style scoped>
.page-container { padding: 2rem; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.table-wrapper { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table th, .styled-table td { padding: 12px 15px; border-bottom: 1px solid #ddd; text-align: left; }
.text-success { color: #28a745; }
.text-danger { color: #dc3545; }
.btn-edit { color: #007bff; text-decoration: none; }
.loading-state, .error-message, .no-data-message { text-align: center; padding: 2rem; }
.btn-primary { 
  background-color: #007bff; 
  color: white; 
  padding: 10px 15px; 
  border-radius: 5px; 
  text-decoration: none; 
  font-weight: bold;
}
</style>
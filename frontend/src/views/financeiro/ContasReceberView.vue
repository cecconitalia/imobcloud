<template>
  <div class="page-container">
    <header class="view-header">
      <h1>Contas a Receber</h1>
      <router-link to="/financeiro/transacoes/nova?tipo=RECEITA" class="btn-primary">
        + Adicionar Receita
      </router-link>
    </header>

    <div v-if="stats" class="summary-grid">
      <div class="summary-card pending-revenue">
        <h4>Total a Receber (Pendente)</h4>
        <p>{{ formatarValor(stats.total_a_receber) }}</p>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">A carregar...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div class="table-card">
      <div v-if="transacoes.length">
        <table class="styled-table">
          <thead>
            <tr>
              <th>Vencimento</th>
              <th>Cliente</th>
              <th>Descrição</th>
              <th class="text-right">Valor</th>
              <th class="text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="transacao in transacoes" :key="transacao.id">
              <td>{{ formatarData(transacao.data_vencimento) }}</td>
              <td>{{ transacao.cliente?.nome_completo || 'N/A' }}</td>
              <td>{{ transacao.descricao }}</td>
              <td class="text-right text-success">{{ formatarValor(transacao.valor) }}</td>
              <td class="text-center">
                <span :class="['status-badge', getStatusClass(transacao.status)]">
                  {{ transacao.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="!isLoading" class="no-data-message">
        Nenhuma conta a receber encontrada.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const transacoes = ref<any[]>([]);
const stats = ref<any>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

const formatarValor = (valor: number) => valor ? valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : 'R$ 0,00';
const formatarData = (data: string) => new Date(data + 'T00:00:00').toLocaleDateString('pt-BR');

const getStatusClass = (status: string) => {
  switch (status) {
    case 'PENDENTE': return 'status-pending';
    case 'ATRASADO': return 'status-overdue';
    case 'PAGO': return 'status-paid';
    default: return '';
  }
};

async function fetchData() {
  isLoading.value = true;
  error.value = null;
  try {
    const [transacoesResponse, statsResponse] = await Promise.all([
      apiClient.get('/v1/financeiro/transacoes/a-receber/'),
      apiClient.get('/v1/financeiro/transacoes/contas-pendentes-stats/')
    ]);
    transacoes.value = transacoesResponse.data;
    stats.value = statsResponse.data;
  } catch (err) {
    console.error("Erro ao buscar dados de contas a receber:", err);
    error.value = "Não foi possível carregar os dados.";
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.page-container { padding: 2rem; max-width: 1200px; margin: auto; }
.view-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.btn-primary { background-color: #007bff; color: white; padding: 12px 18px; border-radius: 6px; text-decoration: none; font-weight: bold; }

.summary-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; margin-bottom: 2rem; }
.summary-card { padding: 1.5rem; border-radius: 8px; background-color: #fff; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid; }
.summary-card h4 { margin: 0 0 0.5rem 0; font-size: 1rem; color: #6c757d; }
.summary-card p { margin: 0; font-size: 2.2rem; font-weight: bold; }
.pending-revenue { border-color: #ffc107; }

.table-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.styled-table { width: 100%; border-collapse: collapse; }
.styled-table th { padding: 1rem; text-align: left; border-bottom: 2px solid #dee2e6; color: #495057; }
.styled-table td { padding: 1rem; border-bottom: 1px solid #e9ecef; }

.text-right { text-align: right; }
.text-center { text-align: center; }
.text-success { color: #28a745; font-weight: bold; }

.status-badge { padding: 0.3rem 0.6rem; border-radius: 12px; font-size: 0.8rem; font-weight: bold; color: white; }
.status-pending { background-color: #ffc107; }
.status-overdue { background-color: #dc3545; }
.status-paid { background-color: #28a745; }

.loading-state, .error-message, .no-data-message { text-align: center; padding: 2rem; color: #6c757d; }
.error-message { color: #dc3545; }
</style>
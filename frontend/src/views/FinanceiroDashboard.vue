<template>
  <div class="financeiro-dashboard-container">
    <header class="view-header">
      <h1>Dashboard Financeiro</h1>
      <div class="header-actions">
        <router-link to="/financeiro/transacoes/nova" class="btn-primary">
          + Adicionar Transação
        </router-link>
        <router-link to="/financeiro/contas" class="btn-secondary">
          Gerir Contas
        </router-link>
        <router-link to="/financeiro/categorias" class="btn-secondary">
          Gerir Categorias
        </router-link>
      </div>
    </header>

    <div v-if="isLoading" class="loading-message">
      A carregar dados financeiros...
    </div>
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="stats" class="stats-grid">
      <div class="stat-card revenue">
        <h3 class="stat-title">Total de Receitas (Mês)</h3>
        <p class="stat-value">{{ formatarValor(stats.receitas_mes) }}</p>
      </div>
      <div class="stat-card expenses">
        <h3 class="stat-title">Total de Despesas (Mês)</h3>
        <p class="stat-value">{{ formatarValor(stats.despesas_mes) }}</p>
      </div>
      <div class="stat-card balance">
        <h3 class="stat-title">Saldo (Mês)</h3>
        <p class="stat-value">{{ formatarValor(stats.saldo_mes) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import apiClient from '@/services/api';

const stats = ref<any>(null);
const isLoading = ref(true);
const error = ref<string | null>(null);

function formatarValor(valor: number | null) {
  if (valor === null) return 'R$ 0,00';
  return parseFloat(valor.toString()).toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });
}

async function fetchStats() {
  isLoading.value = true;
  try {
    // ESTA ROTA AINDA NÃO EXISTE NO BACKEND, mas assumimos que irá existir
    const response = await apiClient.get('/v1/financeiro/stats/');
    stats.value = response.data;
  } catch (err) {
    console.error("Erro ao buscar estatísticas financeiras:", err);
    error.value = 'Não foi possível carregar as estatísticas financeiras.';
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  fetchStats();
});
</script>

<style scoped>
.financeiro-dashboard-container {
  padding: 2rem;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.header-actions {
  display: flex;
  gap: 1rem;
}
.btn-primary, .btn-secondary {
  padding: 10px 15px;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  border: none;
  cursor: pointer;
}
.btn-primary {
  background-color: #007bff;
  color: white;
}
.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}
.stat-card {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}
.stat-card.revenue {
  border-left: 5px solid #28a745;
}
.stat-card.expenses {
  border-left: 5px solid #dc3545;
}
.stat-card.balance {
  border-left: 5px solid #007bff;
}
.stat-title {
  font-size: 1rem;
  color: #6c757d;
  margin-top: 0;
  margin-bottom: 0.5rem;
}
.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #343a40;
  margin: 0;
}
.loading-message, .error-message {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}
.error-message {
  color: red;
}
</style>